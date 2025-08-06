import anthropic
import re
import random
from typing import List, Optional, Dict, Any

class AIGenerator:
    """Handles interactions with Anthropic's Claude API for generating responses"""
    
    # Static system prompt to avoid rebuilding on each call
    SYSTEM_PROMPT = """ You are an AI assistant specialized in course materials and educational content with access to a comprehensive search tool for course information.

Search Tool Usage:
- Use the search tool **only** for questions about specific course content or detailed educational materials
- **One search per query maximum**
- Synthesize search results into accurate, fact-based responses
- If search yields no results, state this clearly without offering alternatives

Response Protocol:
- **General knowledge questions**: Answer using existing knowledge without searching
- **Course-specific questions**: Search first, then answer
- **No meta-commentary**:
 - Provide direct answers only — no reasoning process, search explanations, or question-type analysis
 - Do not mention "based on the search results"


All responses must be:
1. **Brief, Concise and focused** - Get to the point quickly
2. **Educational** - Maintain instructional value
3. **Clear** - Use accessible language
4. **Example-supported** - Include relevant examples when they aid understanding
Provide only the direct answer to what was asked.
"""
    
    def __init__(self, api_key: str, model: str, mock_mode: bool = False):
        self.mock_mode = mock_mode
        self.model = model
        
        # Only initialize Anthropic client if not in mock mode
        if not mock_mode:
            self.client = anthropic.Anthropic(api_key=api_key)
            # Pre-build base API parameters
            self.base_params = {
                "model": self.model,
                "temperature": 0,
                "max_tokens": 800
            }
        
        # Mock responses for different query patterns
        self.mock_responses = {
            "outline": {
                "MCP": """# MCP: Build Rich-Context AI Apps with Anthropic Course Outline

## Lesson 1: Introduction to MCP
- Overview of Model Context Protocol
- Setting up the development environment
- Key concepts and terminology

## Lesson 2: Basic MCP Implementation
- Creating your first MCP server
- Understanding client-server architecture
- Basic communication patterns

## Lesson 3: Advanced Features
- Tool integration and custom functions
- Resource management and optimization
- Error handling and debugging

## Lesson 4: Building Real Applications
- Practical implementation examples
- Integration with existing systems
- Best practices and patterns

## Lesson 5: Deployment and Scaling
- Production deployment strategies
- Performance optimization
- Monitoring and maintenance""",
                "default": """# Course Outline

## Module 1: Foundations
- Core concepts and terminology
- Setting up the environment
- Basic implementation patterns

## Module 2: Implementation
- Hands-on development
- Key features and capabilities
- Integration techniques

## Module 3: Advanced Topics
- Optimization strategies
- Complex scenarios and solutions
- Best practices

## Module 4: Real-World Applications
- Case studies and examples
- Production considerations
- Troubleshooting and maintenance"""
            },
            "chatbot": "Yes, several courses include chatbot implementations. The 'MCP: Build Rich-Context AI Apps with Anthropic' course covers building AI applications that can serve as intelligent chatbots. The course teaches how to create context-aware conversational systems using Anthropic's tools and the Model Context Protocol.",
            "rag": "RAG (Retrieval-Augmented Generation) is explained in the 'Advanced Retrieval for AI with Chroma' course. RAG combines information retrieval with language generation to provide more accurate and contextual responses by first retrieving relevant information from a knowledge base, then using that information to generate informed answers.",
            "lesson": "Lesson 5 of the MCP course covers 'Deployment and Scaling'. This lesson focuses on production deployment strategies, performance optimization techniques, and how to monitor and maintain MCP applications in real-world environments. Students learn about scaling considerations and best practices for enterprise deployment.",
            "default": "I'm a course materials assistant running in demonstration mode. I can help you with questions about course content, outlines, and educational materials. The system has information about courses covering topics like MCP (Model Context Protocol), RAG (Retrieval-Augmented Generation), Chroma database, and Anthropic's AI tools."
        }
        
        # Keywords to detect query types
        self.query_patterns = {
            "outline": ["outline", "structure", "syllabus", "overview", "contents"],
            "chatbot": ["chatbot", "chat bot", "conversational", "bot"],
            "rag": ["rag", "retrieval", "augmented", "generation"],
            "lesson": ["lesson", "module", "chapter", "section"]
        }
    
    def _generate_mock_response(self, query: str, tool_manager=None) -> str:
        """Generate a mock response based on query patterns"""
        query_lower = query.lower()
        
        # Simulate tool usage for course-specific queries
        if tool_manager and any(keyword in query_lower for keyword in ["course", "mcp", "rag", "chroma", "anthropic"]):
            # Simulate a search tool call
            if hasattr(tool_manager, 'execute_tool'):
                try:
                    # This will add mock sources to the tool manager
                    tool_manager.execute_tool("search_courses", query=query)
                except Exception:
                    pass  # Ignore tool execution errors in mock mode
        
        # Check for query patterns and return appropriate mock response
        for pattern_type, keywords in self.query_patterns.items():
            if any(keyword in query_lower for keyword in keywords):
                if pattern_type == "outline":
                    # Check if it's specifically about MCP
                    if "mcp" in query_lower:
                        return self.mock_responses["outline"]["MCP"]
                    else:
                        return self.mock_responses["outline"]["default"]
                else:
                    return self.mock_responses[pattern_type]
        
        # Default response
        return self.mock_responses["default"]
    
    def generate_response(self, query: str,
                         conversation_history: Optional[str] = None,
                         tools: Optional[List] = None,
                         tool_manager=None) -> str:
        """
        Generate AI response with optional tool usage and conversation context.
        
        Args:
            query: The user's question or request
            conversation_history: Previous messages for context
            tools: Available tools the AI can use
            tool_manager: Manager to execute tools
            
        Returns:
            Generated response as string
        """
        
        # Use mock response if in mock mode
        if self.mock_mode:
            return self._generate_mock_response(query, tool_manager)
        
        # Build system content efficiently - avoid string ops when possible
        system_content = (
            f"{self.SYSTEM_PROMPT}\n\nPrevious conversation:\n{conversation_history}"
            if conversation_history 
            else self.SYSTEM_PROMPT
        )
        
        # Prepare API call parameters efficiently
        api_params = {
            **self.base_params,
            "messages": [{"role": "user", "content": query}],
            "system": system_content
        }
        
        # Add tools if available
        if tools:
            api_params["tools"] = tools
            api_params["tool_choice"] = {"type": "auto"}
        
        # Get response from Claude
        response = self.client.messages.create(**api_params)
        
        # Handle tool execution if needed
        if response.stop_reason == "tool_use" and tool_manager:
            return self._handle_tool_execution(response, api_params, tool_manager)
        
        # Return direct response
        return response.content[0].text
    
    def _handle_tool_execution(self, initial_response, base_params: Dict[str, Any], tool_manager):
        """
        Handle execution of tool calls and get follow-up response.
        
        Args:
            initial_response: The response containing tool use requests
            base_params: Base API parameters
            tool_manager: Manager to execute tools
            
        Returns:
            Final response text after tool execution
        """
        # Start with existing messages
        messages = base_params["messages"].copy()
        
        # Add AI's tool use response
        messages.append({"role": "assistant", "content": initial_response.content})
        
        # Execute all tool calls and collect results
        tool_results = []
        for content_block in initial_response.content:
            if content_block.type == "tool_use":
                tool_result = tool_manager.execute_tool(
                    content_block.name, 
                    **content_block.input
                )
                
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": content_block.id,
                    "content": tool_result
                })
        
        # Add tool results as single message
        if tool_results:
            messages.append({"role": "user", "content": tool_results})
        
        # Prepare final API call without tools
        final_params = {
            **self.base_params,
            "messages": messages,
            "system": base_params["system"]
        }
        
        # Get final response
        final_response = self.client.messages.create(**final_params)
        return final_response.content[0].text