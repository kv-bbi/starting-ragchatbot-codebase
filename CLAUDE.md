# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Course Materials RAG (Retrieval-Augmented Generation) System - a full-stack web application that allows users to query course materials and receive AI-powered responses using ChromaDB for vector storage and Anthropic's Claude for generation.

## Development Environment

- **Python Version**: 3.13+
- **Package Manager**: uv (not pip/venv)
- **Environment Variables**: Uses `.env` file with `ANTHROPIC_API_KEY` and optional `MOCK_MODE`

## Common Commands

### Start Application
```bash
# Quick start (recommended)
chmod +x run.sh
./run.sh

# Manual start
cd backend && uv run uvicorn app:app --reload --port 8000
```

### Dependency Management
```bash
# Install dependencies
uv sync

# Add new dependency
uv add <package>
```

### Environment Setup
Create `.env` file in root with:
```bash
ANTHROPIC_API_KEY=your_key_here
MOCK_MODE=true  # Optional: for demo without API calls
```

## System Architecture

### Core Components
- **Frontend**: Vanilla HTML/JS/CSS served as static files
- **Backend**: FastAPI application with modular architecture
- **Vector Store**: ChromaDB with sentence-transformers embedding
- **AI Integration**: Anthropic Claude API with tool usage

### Backend Module Structure
- `app.py`: FastAPI application and endpoints
- `rag_system.py`: Main orchestrator connecting all components
- `ai_generator.py`: Anthropic API integration with tool support
- `vector_store.py`: ChromaDB operations and semantic search
- `search_tools.py`: Tool system for Claude function calling
- `document_processor.py`: Course content chunking and processing
- `session_manager.py`: Conversation history management
- `config.py`: Environment and configuration management
- `models.py`: Pydantic data models

### Data Flow
1. Frontend sends query to `/api/query` endpoint
2. `RAGSystem.query()` orchestrates processing
3. `AIGenerator.generate_response()` makes Claude API calls
4. Tools execute semantic search when needed
5. Response returns with sources to frontend

### Key Features
- **Mock Mode**: Set `MOCK_MODE=true` to simulate API responses without actual Anthropic API calls
- **Session Management**: Maintains conversation history per session
- **Tool Integration**: Claude can search course content using function calling
- **Static File Serving**: Frontend served directly by FastAPI

### Vector Store Implementation
- Uses ChromaDB with `all-MiniLM-L6-v2` embedding model
- Course documents chunked into 800-character segments with 100-character overlap
- Supports both course metadata and content search

### Configuration
All settings centralized in `config.py` with environment variable overrides:
- Anthropic model: `claude-3-5-haiku-20241022`
- Chunk size: 800 characters
- Max search results: 5
- Conversation history: 2 messages

## Development Notes

- The system is designed for course material indexing and querying
- ChromaDB data persists in `backend/chroma_db/`
- Course content loaded from `docs/` directory
- Frontend uses vanilla JavaScript with markdown rendering
- No build process required - static files served directly