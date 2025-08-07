"""Test configuration and shared fixtures for the RAG system tests."""

import os
import sys
import pytest
from unittest.mock import Mock, AsyncMock, patch
from typing import AsyncGenerator, Dict, Any, List
import tempfile
import shutil
from pathlib import Path

# Add the backend directory to the Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from config import Config
from models import Course, Lesson, CourseChunk
from session_manager import SessionManager

# Import test-specific models
from .test_data_models import QueryRequest, QueryResponse, CourseStats
from vector_store import VectorStore
from ai_generator import AIGenerator
from rag_system import RAGSystem


@pytest.fixture
def test_config():
    """Create a test configuration with safe defaults."""
    return Config(
        anthropic_api_key="test-key",
        mock_mode=True,
        chunk_size=800,
        chunk_overlap=100,
        max_search_results=5,
        max_conversation_history=2,
        anthropic_model="claude-3-5-haiku-20241022"
    )


@pytest.fixture
def temp_docs_dir():
    """Create a temporary directory with test documents."""
    temp_dir = tempfile.mkdtemp()
    
    # Create test course files
    course1_dir = Path(temp_dir) / "Course 1"
    course1_dir.mkdir()
    
    (course1_dir / "lesson1.txt").write_text(
        "This is lesson 1 content about machine learning basics. "
        "Machine learning is a subset of artificial intelligence."
    )
    
    (course1_dir / "lesson2.txt").write_text(
        "This is lesson 2 content about neural networks. "
        "Neural networks are inspired by biological neural networks."
    )
    
    course2_dir = Path(temp_dir) / "Course 2"
    course2_dir.mkdir()
    
    (course2_dir / "intro.txt").write_text(
        "Introduction to data science and statistics. "
        "Data science combines domain expertise with programming skills."
    )
    
    yield temp_dir
    
    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def temp_chroma_dir():
    """Create a temporary ChromaDB directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_anthropic_client():
    """Mock Anthropic client for testing."""
    mock_client = Mock()
    mock_message = Mock()
    mock_message.content = [Mock(text="This is a test response from Claude.")]
    mock_message.stop_reason = "end_turn"
    
    mock_client.messages.create = AsyncMock(return_value=mock_message)
    return mock_client


@pytest.fixture
def mock_session_manager():
    """Mock session manager for testing."""
    mock_manager = Mock()
    mock_manager.create_session.return_value = "test-session-123"
    mock_manager.add_message.return_value = None
    mock_manager.get_conversation_history.return_value = []
    return mock_manager


@pytest.fixture
def mock_vector_store():
    """Mock vector store for testing."""
    mock_store = Mock()
    mock_store.search.return_value = [
        {
            "content": "This is test content about machine learning.",
            "source": "Course 1/lesson1.txt",
            "distance": 0.1
        },
        {
            "content": "Neural networks are computational models.",
            "source": "Course 1/lesson2.txt", 
            "distance": 0.2
        }
    ]
    mock_store.get_collection_stats.return_value = {
        "total_chunks": 10,
        "unique_sources": 3
    }
    return mock_store


@pytest.fixture
def mock_ai_generator(mock_anthropic_client):
    """Mock AI generator for testing."""
    mock_generator = Mock()
    mock_generator.generate_response = AsyncMock(
        return_value="This is a test response from the AI generator."
    )
    mock_generator.client = mock_anthropic_client
    return mock_generator


@pytest.fixture
def mock_rag_system(mock_session_manager, mock_vector_store, mock_ai_generator):
    """Mock RAG system for testing."""
    mock_system = Mock()
    mock_system.session_manager = mock_session_manager
    mock_system.vector_store = mock_vector_store
    mock_system.ai_generator = mock_ai_generator
    
    mock_system.query = AsyncMock(return_value=(
        "This is a test answer about machine learning.",
        ["Course 1/lesson1.txt", "Course 1/lesson2.txt"]
    ))
    
    mock_system.get_course_analytics.return_value = {
        "total_courses": 2,
        "course_titles": ["Course 1", "Course 2"]
    }
    
    mock_system.add_course_folder.return_value = (2, 10)
    
    return mock_system


@pytest.fixture
def sample_query_request():
    """Sample query request for testing."""
    return QueryRequest(
        query="What is machine learning?",
        session_id="test-session-123"
    )


@pytest.fixture
def sample_query_response():
    """Sample query response for testing."""
    return QueryResponse(
        answer="Machine learning is a subset of artificial intelligence.",
        sources=["Course 1/lesson1.txt", "Course 1/lesson2.txt"],
        session_id="test-session-123"
    )


@pytest.fixture
def sample_course_stats():
    """Sample course statistics for testing."""
    return CourseStats(
        total_courses=2,
        course_titles=["Course 1", "Course 2"]
    )


@pytest.fixture
def mock_os_path_exists():
    """Mock os.path.exists to control file system checks."""
    with patch('os.path.exists') as mock_exists:
        mock_exists.return_value = True
        yield mock_exists


@pytest.fixture
def mock_startup_document_loading():
    """Mock document loading during startup to avoid side effects."""
    with patch('app.rag_system.add_course_folder') as mock_add:
        mock_add.return_value = (2, 10)
        yield mock_add


@pytest.fixture
def test_documents():
    """Sample test documents for vector store testing."""
    return [
        {
            "content": "Machine learning is a method of data analysis that automates analytical model building.",
            "source": "ml_basics.txt",
            "course": "AI Fundamentals"
        },
        {
            "content": "Neural networks are computing systems vaguely inspired by biological neural networks.",
            "source": "neural_networks.txt", 
            "course": "Deep Learning"
        },
        {
            "content": "Statistics is the discipline that concerns the collection and analysis of data.",
            "source": "statistics_intro.txt",
            "course": "Data Science"
        }
    ]


# Environment variables for testing
@pytest.fixture(autouse=True)
def setup_test_env():
    """Set up test environment variables."""
    os.environ["MOCK_MODE"] = "true"
    os.environ["ANTHROPIC_API_KEY"] = "test-key"
    yield
    # Cleanup is handled by pytest automatically