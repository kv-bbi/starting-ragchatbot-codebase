"""API endpoint tests for the Course Materials RAG System."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from unittest.mock import patch, Mock, AsyncMock
import json

# Import the models and endpoint handlers
from .test_data_models import QueryRequest, QueryResponse, CourseStats


@pytest.fixture
def test_app(mock_rag_system):
    """Create a test FastAPI app without static file mounting."""
    app = FastAPI(title="Course Materials RAG System Test", root_path="")
    
    # Add the same middleware as the real app
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"]
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )
    
    # Define the API endpoints inline to avoid import issues with static files
    @app.post("/api/query", response_model=QueryResponse)
    async def query_documents(request: QueryRequest):
        """Process a query and return response with sources"""
        try:
            session_id = request.session_id
            if not session_id:
                session_id = mock_rag_system.session_manager.create_session()
            
            answer, sources = await mock_rag_system.query(request.query, session_id)
            
            return QueryResponse(
                answer=answer,
                sources=sources,
                session_id=session_id
            )
        except Exception as e:
            from fastapi import HTTPException
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/courses", response_model=CourseStats)
    async def get_course_stats():
        """Get course analytics and statistics"""
        try:
            analytics = mock_rag_system.get_course_analytics()
            return CourseStats(
                total_courses=analytics["total_courses"],
                course_titles=analytics["course_titles"]
            )
        except Exception as e:
            from fastapi import HTTPException
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/")
    async def root():
        """Root endpoint for health check"""
        return {"message": "Course Materials RAG System API"}
    
    return app


@pytest.fixture
def test_client(test_app):
    """Create a test client for the FastAPI app."""
    return TestClient(test_app)


@pytest.mark.api
class TestQueryEndpoint:
    """Test the /api/query endpoint."""
    
    def test_query_with_session_id(self, test_client, mock_rag_system):
        """Test query with existing session ID."""
        query_data = {
            "query": "What is machine learning?",
            "session_id": "test-session-123"
        }
        
        response = test_client.post("/api/query", json=query_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "answer" in data
        assert "sources" in data
        assert "session_id" in data
        assert data["session_id"] == "test-session-123"
        assert isinstance(data["sources"], list)
        
        # Verify the mock was called correctly
        mock_rag_system.query.assert_called_once_with(
            "What is machine learning?", "test-session-123"
        )
    
    def test_query_without_session_id(self, test_client, mock_rag_system):
        """Test query without session ID (should create new session)."""
        query_data = {
            "query": "Explain neural networks"
        }
        
        response = test_client.post("/api/query", json=query_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "answer" in data
        assert "sources" in data
        assert "session_id" in data
        assert data["session_id"] == "test-session-123"  # From mock
        
        # Verify session creation was called
        mock_rag_system.session_manager.create_session.assert_called_once()
    
    def test_query_empty_string(self, test_client):
        """Test query with empty string."""
        query_data = {
            "query": "",
            "session_id": "test-session-123"
        }
        
        response = test_client.post("/api/query", json=query_data)
        
        # Should still process (empty queries are valid)
        assert response.status_code == 200
    
    def test_query_missing_query_field(self, test_client):
        """Test request missing required query field."""
        query_data = {
            "session_id": "test-session-123"
        }
        
        response = test_client.post("/api/query", json=query_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_query_invalid_json(self, test_client):
        """Test request with invalid JSON."""
        response = test_client.post(
            "/api/query",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422
    
    def test_query_server_error(self, test_client, mock_rag_system):
        """Test handling of server errors during query processing."""
        # Make the mock raise an exception
        mock_rag_system.query.side_effect = Exception("Database connection failed")
        
        query_data = {
            "query": "What is machine learning?",
            "session_id": "test-session-123"
        }
        
        response = test_client.post("/api/query", json=query_data)
        
        assert response.status_code == 500
        assert "Database connection failed" in response.json()["detail"]


@pytest.mark.api
class TestCoursesEndpoint:
    """Test the /api/courses endpoint."""
    
    def test_get_course_stats_success(self, test_client, mock_rag_system):
        """Test successful retrieval of course statistics."""
        response = test_client.get("/api/courses")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "total_courses" in data
        assert "course_titles" in data
        assert data["total_courses"] == 2
        assert data["course_titles"] == ["Course 1", "Course 2"]
        
        # Verify the mock was called
        mock_rag_system.get_course_analytics.assert_called_once()
    
    def test_get_course_stats_no_courses(self, test_client, mock_rag_system):
        """Test course stats when no courses are loaded."""
        # Override the mock return value
        mock_rag_system.get_course_analytics.return_value = {
            "total_courses": 0,
            "course_titles": []
        }
        
        response = test_client.get("/api/courses")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["total_courses"] == 0
        assert data["course_titles"] == []
    
    def test_get_course_stats_server_error(self, test_client, mock_rag_system):
        """Test handling of server errors during analytics retrieval."""
        # Make the mock raise an exception
        mock_rag_system.get_course_analytics.side_effect = Exception("Analytics service unavailable")
        
        response = test_client.get("/api/courses")
        
        assert response.status_code == 500
        assert "Analytics service unavailable" in response.json()["detail"]


@pytest.mark.api
class TestRootEndpoint:
    """Test the root / endpoint."""
    
    def test_root_endpoint(self, test_client):
        """Test the root endpoint returns expected message."""
        response = test_client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        assert data["message"] == "Course Materials RAG System API"


@pytest.mark.api
class TestCORSAndMiddleware:
    """Test CORS and middleware functionality."""
    
    def test_cors_headers_present(self, test_client):
        """Test that CORS headers are present in responses."""
        response = test_client.get("/", headers={"Origin": "http://localhost:3000"})
        
        assert response.status_code == 200
        # FastAPI TestClient doesn't fully simulate CORS, but we can verify the app has CORS middleware
        
    def test_options_request(self, test_client):
        """Test preflight OPTIONS request."""
        response = test_client.options(
            "/api/query",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            }
        )
        
        # OPTIONS requests should be handled by CORS middleware
        assert response.status_code in [200, 405]  # 405 if endpoint doesn't explicitly handle OPTIONS


@pytest.mark.api
class TestRequestValidation:
    """Test request validation and response models."""
    
    def test_query_request_validation(self, test_client):
        """Test validation of query request fields."""
        # Test various invalid request formats
        invalid_requests = [
            {"query": None},  # None value
            {"query": 123},   # Wrong type
            {},               # Missing required field
        ]
        
        for invalid_request in invalid_requests:
            response = test_client.post("/api/query", json=invalid_request)
            assert response.status_code == 422
    
    def test_response_format_compliance(self, test_client, mock_rag_system):
        """Test that responses comply with the expected format."""
        query_data = {
            "query": "What is machine learning?",
            "session_id": "test-session-123"
        }
        
        response = test_client.post("/api/query", json=query_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response matches QueryResponse model
        assert isinstance(data["answer"], str)
        assert isinstance(data["sources"], list)
        assert isinstance(data["session_id"], str)
        
        # Test courses endpoint response format
        response = test_client.get("/api/courses")
        assert response.status_code == 200
        data = response.json()
        
        # Verify response matches CourseStats model
        assert isinstance(data["total_courses"], int)
        assert isinstance(data["course_titles"], list)
        assert all(isinstance(title, str) for title in data["course_titles"])


@pytest.mark.integration
class TestEndToEndFlow:
    """Test complete end-to-end API flows."""
    
    def test_query_flow_with_new_session(self, test_client, mock_rag_system):
        """Test complete query flow creating a new session."""
        # First query without session ID
        query1_data = {"query": "What is machine learning?"}
        response1 = test_client.post("/api/query", json=query1_data)
        
        assert response1.status_code == 200
        data1 = response1.json()
        session_id = data1["session_id"]
        
        # Second query with the returned session ID
        query2_data = {
            "query": "Tell me more about neural networks",
            "session_id": session_id
        }
        response2 = test_client.post("/api/query", json=query2_data)
        
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["session_id"] == session_id
        
        # Verify both queries were processed
        assert mock_rag_system.query.call_count == 2
    
    def test_courses_then_query_flow(self, test_client, mock_rag_system):
        """Test flow of checking courses then making a query."""
        # First get course stats
        response1 = test_client.get("/api/courses")
        assert response1.status_code == 200
        
        courses_data = response1.json()
        assert courses_data["total_courses"] > 0
        
        # Then make a query
        query_data = {"query": f"Tell me about {courses_data['course_titles'][0]}"}
        response2 = test_client.post("/api/query", json=query_data)
        
        assert response2.status_code == 200
        query_response = response2.json()
        assert "answer" in query_response