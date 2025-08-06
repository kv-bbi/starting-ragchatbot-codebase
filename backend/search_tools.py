from typing import Dict, Any, Optional, Protocol
from abc import ABC, abstractmethod
from vector_store import VectorStore, SearchResults


class Tool(ABC):
    """Abstract base class for all tools"""
    
    @abstractmethod
    def get_tool_definition(self) -> Dict[str, Any]:
        """Return Anthropic tool definition for this tool"""
        pass
    
    @abstractmethod
    def execute(self, **kwargs) -> str:
        """Execute the tool with given parameters"""
        pass


class CourseSearchTool(Tool):
    """Tool for searching course content with semantic course name matching"""
    
    def __init__(self, vector_store: VectorStore):
        self.store = vector_store
        self.last_sources = []  # Track sources from last search
        # Mock sources for demonstration mode
        self.mock_sources = [
            "MCP Course - Lesson 1: Introduction",
            "MCP Course - Lesson 5: Deployment",
            "Advanced Retrieval Course - Module 2",
            "Anthropic API Documentation"
        ]
    
    def get_tool_definition(self) -> Dict[str, Any]:
        """Return Anthropic tool definition for this tool"""
        return {
            "name": "search_course_content",
            "description": "Search course materials with smart course name matching and lesson filtering",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string", 
                        "description": "What to search for in the course content"
                    },
                    "course_name": {
                        "type": "string",
                        "description": "Course title (partial matches work, e.g. 'MCP', 'Introduction')"
                    },
                    "lesson_number": {
                        "type": "integer",
                        "description": "Specific lesson number to search within (e.g. 1, 2, 3)"
                    }
                },
                "required": ["query"]
            }
        }
    
    def execute(self, query: str, course_name: Optional[str] = None, lesson_number: Optional[int] = None) -> str:
        """
        Execute the search tool with given parameters.
        
        Args:
            query: What to search for
            course_name: Optional course filter
            lesson_number: Optional lesson filter
            
        Returns:
            Formatted search results or error message
        """
        
        # Use the vector store's unified search interface
        results = self.store.search(
            query=query,
            course_name=course_name,
            lesson_number=lesson_number
        )
        
        # Handle errors
        if results.error:
            return results.error
        
        # Handle empty results
        if results.is_empty():
            filter_info = ""
            if course_name:
                filter_info += f" in course '{course_name}'"
            if lesson_number:
                filter_info += f" in lesson {lesson_number}"
            return f"No relevant content found{filter_info}."
        
        # Format and return results
        return self._format_results(results)
    
    def execute_mock(self, query: str, course_name: Optional[str] = None, lesson_number: Optional[int] = None) -> str:
        """Execute mock search for demonstration purposes"""
        import random
        
        # Set mock sources with new structure
        mock_sources_data = [
            {"text": "MCP Course - Lesson 1: Introduction", "url": "https://example.com/mcp-lesson-1"},
            {"text": "MCP Course - Lesson 5: Deployment", "url": "https://example.com/mcp-lesson-5"},
            {"text": "Advanced Retrieval Course - Module 2", "url": None},
            {"text": "Anthropic API Documentation", "url": None}
        ]
        self.last_sources = random.sample(mock_sources_data, min(2, len(mock_sources_data)))
        
        # Generate mock response based on query
        if "outline" in query.lower() and course_name and "mcp" in course_name.lower():
            return """**MCP Course Outline Found:**
            
Lesson 1: Introduction to MCP
- Model Context Protocol overview
- Development environment setup
- Core concepts

Lesson 5: Deployment and Scaling  
- Production deployment strategies
- Performance optimization
- Monitoring and maintenance"""
        
        elif "lesson" in query.lower() and lesson_number == 5:
            return """**Lesson 5: Deployment and Scaling**
            
This lesson covers:
- Production deployment strategies for MCP applications
- Performance optimization techniques
- Monitoring and maintenance best practices
- Enterprise scaling considerations"""
        
        else:
            return f"""**Mock Search Results for: {query}**
            
Found relevant information about course materials. This is demonstration mode - 
the system would normally search through actual course content to provide 
specific answers about lessons, outlines, and course materials."""
    
    def _format_results(self, results: SearchResults) -> str:
        """Format search results with course and lesson context"""
        formatted = []
        sources = []  # Track sources for the UI
        
        for doc, meta in zip(results.documents, results.metadata):
            course_title = meta.get('course_title', 'unknown')
            lesson_num = meta.get('lesson_number')
            
            # Build context header
            header = f"[{course_title}"
            if lesson_num is not None:
                header += f" - Lesson {lesson_num}"
            header += "]"
            
            # Build source for the UI with link data
            source_text = course_title
            if lesson_num is not None:
                source_text += f" - Lesson {lesson_num}"
            
            # Try to get lesson link if we have lesson number
            source_data = {"text": source_text, "url": None}
            if lesson_num is not None and course_title != 'unknown':
                lesson_link = self.store.get_lesson_link(course_title, lesson_num)
                if lesson_link:
                    source_data["url"] = lesson_link
            
            sources.append(source_data)
            formatted.append(f"{header}\n{doc}")
        
        # Store sources for retrieval
        self.last_sources = sources
        
        return "\n\n".join(formatted)

class ToolManager:
    """Manages available tools for the AI"""
    
    def __init__(self, mock_mode: bool = False):
        self.tools = {}
        self.mock_mode = mock_mode
    
    def register_tool(self, tool: Tool):
        """Register any tool that implements the Tool interface"""
        tool_def = tool.get_tool_definition()
        tool_name = tool_def.get("name")
        if not tool_name:
            raise ValueError("Tool must have a 'name' in its definition")
        self.tools[tool_name] = tool

    
    def get_tool_definitions(self) -> list:
        """Get all tool definitions for Anthropic tool calling"""
        return [tool.get_tool_definition() for tool in self.tools.values()]
    
    def execute_tool(self, tool_name: str, **kwargs) -> str:
        """Execute a tool by name with given parameters"""
        if tool_name not in self.tools:
            # Handle mock search for unregistered tools in mock mode
            if self.mock_mode and tool_name == "search_courses":
                return self._execute_mock_search(**kwargs)
            return f"Tool '{tool_name}' not found"
        
        # Use mock execution if in mock mode and tool supports it
        if self.mock_mode and hasattr(self.tools[tool_name], 'execute_mock'):
            return self.tools[tool_name].execute_mock(**kwargs)
        
        return self.tools[tool_name].execute(**kwargs)
    
    def _execute_mock_search(self, **kwargs) -> str:
        """Execute a mock search and set mock sources"""
        query = kwargs.get('query', 'general query')
        # Set mock sources for any registered CourseSearchTool
        for tool in self.tools.values():
            if hasattr(tool, 'mock_sources'):
                # Create mock sources with sample URLs for testing
                mock_sources_data = [
                    {"text": "MCP Course - Lesson 1: Introduction", "url": "https://learn.deeplearning.ai/courses/mcp/lesson/1/introduction"},
                    {"text": "MCP Course - Lesson 5: Deployment", "url": "https://learn.deeplearning.ai/courses/mcp/lesson/5/deployment"},
                    {"text": "Advanced Retrieval Course - Module 2", "url": "https://learn.deeplearning.ai/courses/advanced-retrieval/lesson/2"},
                    {"text": "Anthropic API Documentation", "url": "https://docs.anthropic.com/api/overview"}
                ]
                tool.last_sources = mock_sources_data[:2]  # Use first 2 mock sources
                break
        return f"Mock search completed for: {query}"
    
    def get_last_sources(self) -> list:
        """Get sources from the last search operation"""
        # Check all tools for last_sources attribute
        for tool in self.tools.values():
            if hasattr(tool, 'last_sources') and tool.last_sources:
                return tool.last_sources
        return []

    def reset_sources(self):
        """Reset sources from all tools that track sources"""
        for tool in self.tools.values():
            if hasattr(tool, 'last_sources'):
                tool.last_sources = []