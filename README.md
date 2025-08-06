# Course Materials RAG System

A Retrieval-Augmented Generation (RAG) system designed to answer questions about course materials using semantic search and AI-powered responses.

## Overview

This application is a full-stack web application that enables users to query course materials and receive intelligent, context-aware responses. It uses ChromaDB for vector storage, Anthropic's Claude for AI generation, and provides a web interface for interaction.


## Prerequisites

- Python 3.13 or higher
- uv (Python package manager)
- An Anthropic API key (for Claude AI)
- **For Windows**: Use Git Bash to run the application commands - [Download Git for Windows](https://git-scm.com/downloads/win)

## Installation

1. **Install uv** (if not already installed)
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Install Python dependencies**
   ```bash
   uv sync
   ```

3. **Set up environment variables**
   
   Create a `.env` file in the root directory:
   ```bash
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   ```
   
   **For demonstration without API credits:**
   ```bash
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   MOCK_MODE=true
   ```

## Running the Application

### Quick Start

Use the provided shell script:
```bash
chmod +x run.sh
./run.sh
```

### Manual Start

```bash
cd backend
uv run uvicorn app:app --reload --port 8000
```

The application will be available at:
- Web Interface: `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`

## Demo Mode

If you encounter API credit issues or want to test the system without using Anthropic API calls, enable mock mode:

1. **Add to your `.env` file:**
   ```bash
   MOCK_MODE=true
   ```

2. **Restart the application:**
   ```bash
   ./run.sh
   ```

3. **Test with demo queries:**
   - "What is the outline of the MCP course?"
   - "Are there any courses that include a Chatbot implementation?"
   - "What was covered in lesson 5 of the MCP course?"
   - "Are there any courses that explain what RAG is?"

**Mock Mode Features:**
- Bypasses Anthropic API calls completely
- Returns realistic course-related responses
- Includes mock sources for demonstration
- Supports pattern-based query recognition
- Perfect for development and testing

