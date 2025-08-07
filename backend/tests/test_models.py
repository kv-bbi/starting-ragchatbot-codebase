"""Unit tests for Pydantic models."""

import pytest
from pydantic import ValidationError

from .test_data_models import QueryRequest, QueryResponse, CourseStats


@pytest.mark.unit
class TestQueryRequest:
    """Test QueryRequest model validation."""
    
    def test_valid_query_request_with_session(self):
        """Test valid query request with session ID."""
        request = QueryRequest(
            query="What is machine learning?",
            session_id="test-session-123"
        )
        
        assert request.query == "What is machine learning?"
        assert request.session_id == "test-session-123"
    
    def test_valid_query_request_without_session(self):
        """Test valid query request without session ID."""
        request = QueryRequest(query="What is machine learning?")
        
        assert request.query == "What is machine learning?"
        assert request.session_id is None
    
    def test_empty_query_allowed(self):
        """Test that empty query strings are allowed."""
        request = QueryRequest(query="")
        
        assert request.query == ""
        assert request.session_id is None
    
    def test_missing_query_field(self):
        """Test that missing query field raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            QueryRequest()
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("query",)
        assert errors[0]["type"] == "missing"
    
    def test_invalid_query_type(self):
        """Test that non-string query raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            QueryRequest(query=123)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("query",)
        assert "string_type" in errors[0]["type"]


@pytest.mark.unit
class TestQueryResponse:
    """Test QueryResponse model validation."""
    
    def test_valid_query_response_with_string_sources(self):
        """Test valid query response with string sources."""
        response = QueryResponse(
            answer="Machine learning is a subset of AI.",
            sources=["source1.txt", "source2.txt"],
            session_id="test-session-123"
        )
        
        assert response.answer == "Machine learning is a subset of AI."
        assert response.sources == ["source1.txt", "source2.txt"]
        assert response.session_id == "test-session-123"
    
    def test_valid_query_response_with_dict_sources(self):
        """Test valid query response with dictionary sources."""
        sources = [
            {"file": "source1.txt", "relevance": 0.9},
            {"file": "source2.txt", "relevance": 0.8}
        ]
        
        response = QueryResponse(
            answer="Machine learning is a subset of AI.",
            sources=sources,
            session_id="test-session-123"
        )
        
        assert response.answer == "Machine learning is a subset of AI."
        assert response.sources == sources
        assert response.session_id == "test-session-123"
    
    def test_empty_sources_allowed(self):
        """Test that empty sources list is allowed."""
        response = QueryResponse(
            answer="No sources found.",
            sources=[],
            session_id="test-session-123"
        )
        
        assert response.sources == []
    
    def test_missing_required_fields(self):
        """Test that missing required fields raise validation error."""
        with pytest.raises(ValidationError) as exc_info:
            QueryResponse()
        
        errors = exc_info.value.errors()
        required_fields = {error["loc"][0] for error in errors}
        assert "answer" in required_fields
        assert "sources" in required_fields
        assert "session_id" in required_fields


@pytest.mark.unit
class TestCourseStats:
    """Test CourseStats model validation."""
    
    def test_valid_course_stats(self):
        """Test valid course statistics."""
        stats = CourseStats(
            total_courses=3,
            course_titles=["Course 1", "Course 2", "Course 3"]
        )
        
        assert stats.total_courses == 3
        assert stats.course_titles == ["Course 1", "Course 2", "Course 3"]
    
    def test_empty_course_stats(self):
        """Test course stats with no courses."""
        stats = CourseStats(
            total_courses=0,
            course_titles=[]
        )
        
        assert stats.total_courses == 0
        assert stats.course_titles == []
    
    def test_mismatched_count_and_titles(self):
        """Test that mismatched count and titles is allowed (validation at business logic level)."""
        stats = CourseStats(
            total_courses=5,
            course_titles=["Course 1", "Course 2"]  # Only 2 titles but count is 5
        )
        
        # This should be allowed at the model level, business logic should handle validation
        assert stats.total_courses == 5
        assert len(stats.course_titles) == 2
    
    def test_invalid_total_courses_type(self):
        """Test that non-integer total_courses raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            CourseStats(
                total_courses="three",
                course_titles=["Course 1"]
            )
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("total_courses",)
    
    def test_invalid_course_titles_type(self):
        """Test that non-list course_titles raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            CourseStats(
                total_courses=1,
                course_titles="Course 1"  # Should be a list
            )
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("course_titles",)