# Testing Framework for Course Materials RAG System

This directory contains comprehensive tests for the RAG system API endpoints and core functionality.

## Test Structure

- `conftest.py` - Shared fixtures and test configuration
- `test_data_models.py` - Pydantic models used in tests (mirrors app.py models)
- `test_models.py` - Unit tests for Pydantic model validation
- `test_api_endpoints.py` - API endpoint tests for FastAPI routes

## Running Tests

```bash
# Run all tests
uv run pytest tests/

# Run specific test file
uv run pytest tests/test_api_endpoints.py

# Run with verbose output
uv run pytest tests/ -v

# Run tests with coverage (if coverage installed)
uv run pytest tests/ --cov=..

# Run only unit tests
uv run pytest tests/ -m unit

# Run only API tests
uv run pytest tests/ -m api

# Run only integration tests
uv run pytest tests/ -m integration
```

## Test Categories

Tests are organized with pytest markers:

- `@pytest.mark.unit` - Unit tests for individual components
- `@pytest.mark.api` - API endpoint tests
- `@pytest.mark.integration` - End-to-end integration tests

## Key Features

### Fixtures and Mocking

- **Mock RAG System**: Complete mock of the RAG system with all dependencies
- **Mock AI Generator**: Anthropic API client mock for testing without real API calls
- **Mock Vector Store**: ChromaDB mock with sample search results
- **Mock Session Manager**: Session handling mock for conversation management
- **Test Data**: Sample documents and queries for consistent testing

### API Testing

- **FastAPI TestClient**: Uses FastAPI's built-in test client
- **Static File Handling**: Test app configuration avoids static file mounting issues
- **Request/Response Validation**: Tests Pydantic model validation
- **Error Handling**: Tests HTTP error responses and edge cases
- **CORS and Middleware**: Tests middleware functionality

### Test Isolation

- Each test uses fresh mocks to avoid state pollution
- Temporary directories for file-based tests
- Environment variable isolation
- Async test support with pytest-asyncio

## Adding New Tests

1. **Unit Tests**: Add to `test_models.py` or create new `test_<component>.py`
2. **API Tests**: Add to `test_api_endpoints.py` following existing patterns
3. **Fixtures**: Add shared test data and mocks to `conftest.py`
4. **Marks**: Use appropriate pytest markers (`@pytest.mark.unit`, etc.)

## Mock Usage Patterns

```python
# Test an API endpoint
def test_my_endpoint(test_client, mock_rag_system):
    mock_rag_system.query.return_value = ("test answer", ["source1"])
    response = test_client.post("/api/query", json={"query": "test"})
    assert response.status_code == 200

# Test with custom mock behavior
def test_error_handling(test_client, mock_rag_system):
    mock_rag_system.query.side_effect = Exception("Test error")
    response = test_client.post("/api/query", json={"query": "test"})
    assert response.status_code == 500
```

## Configuration

Test configuration is managed through:

- `pyproject.toml` - pytest.ini_options section
- Environment variables automatically set in conftest.py
- Test-specific settings that override production config