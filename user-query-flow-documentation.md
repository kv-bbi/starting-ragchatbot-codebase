# User Query Processing Flow - RAG Chatbot System

## Overview
This document traces the complete flow of a user query from the frontend interface through the backend processing, highlighting where the Anthropic API key is used for Claude API calls.

## System Architecture Flow

### 1. Frontend Query Initiation
**Files**: `frontend/index.html`, `frontend/script.js`

- User enters query in chat input field (`index.html:59-64`)
- JavaScript `sendMessage()` function triggered (`script.js:45`)
- Frontend makes POST request to `/api/query` endpoint (`script.js:63-72`)
- Request includes: `query` and `session_id`

### 2. Backend API Endpoint Reception
**File**: `backend/app.py:56-74`

- FastAPI receives POST request at `/api/query` endpoint
- Creates new session if none provided via `rag_system.session_manager.create_session()`
- Delegates processing to `rag_system.query(request.query, session_id)`

### 3. RAG System Processing
**File**: `backend/rag_system.py:102-140`

- `RAGSystem.query()` method processes user query
- Constructs prompt: `"Answer this question about course materials: {query}"`
- Retrieves conversation history from session (if available)
- **Critical handoff**: Calls `ai_generator.generate_response()` with:
  - Query and conversation history
  - Available search tools
  - Tool manager for execution

### 4. 🔑 Anthropic API Integration Point
**File**: `backend/ai_generator.py`

#### API Key Configuration
- **Environment Loading**: `backend/config.py:15` - `ANTHROPIC_API_KEY` loaded from `.env`
- **Client Initialization**: `ai_generator.py:33` - Creates Anthropic client with API key:
  ```python
  self.client = anthropic.Anthropic(api_key=api_key)
  ```

#### First API Call (`ai_generator.py:80`)
```python
response = self.client.messages.create(**api_params)
```

**API Parameters**:
- Model: `claude-3-5-haiku-20241022`
- Temperature: 0
- Max tokens: 800
- System prompt with course-specific instructions
- User message with query
- Available tools for course search

#### Tool Execution (if needed)
**File**: `ai_generator.py:83-135`

- If Claude uses search tool: `_handle_tool_execution()` called
- Tool searches course content in vector store
- **Second API Call**: `ai_generator.py:134` - Another call with tool results:
  ```python
  final_response = self.client.messages.create(**final_params)
  ```

### 5. Response Flow Back to User
**Files**: `rag_system.py` → `app.py` → `script.js`

- AI response returns to `rag_system.py:122`
- Sources collected from tool manager
- Response and sources returned to `app.py:66`
- FastAPI returns JSON: `{answer, sources, session_id}`
- Frontend receives at `script.js:76`
- Response displayed in chat with markdown rendering

## Visual Flow Diagram

```
┌─────────────────┐    POST /api/query     ┌──────────────────┐
│   Frontend      │ ─────────────────────→ │   Backend API    │
│   script.js:63  │    {query, session_id} │   app.py:56      │
└─────────────────┘                        └──────────────────┘
                                                      │
                                                      │ rag_system.query()
                                                      ▼
                                           ┌──────────────────┐
                                           │   RAG System     │
                                           │ rag_system.py:102│
                                           └──────────────────┘
                                                      │
                                           ai_generator.generate_response()
                                                      │
                                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    🔑 ANTHROPIC API INTEGRATION ZONE                        │
│                                                                             │
│  ┌─────────────────┐    API Key from     ┌──────────────────┐              │
│  │    Config       │ ─────────────────→  │  AI Generator    │              │
│  │  config.py:15   │   .env file         │ ai_generator.py  │              │
│  │                 │                     └──────────────────┘              │
│  │ ANTHROPIC_API_KEY                              │                        │
│  └─────────────────┘                              │                        │
│                                                   │ client.messages.create()│
│                                                   ▼                        │
│                                        ┌──────────────────┐                │
│                                        │  Anthropic API   │                │
│                                        │   Claude Model   │                │
│                                        │ claude-3-5-haiku │                │
│                                        └──────────────────┘                │
│                                                   │                        │
│                              Tool needed?         │                        │
│                                  ┌────────────────┘                        │
│                                  │                                         │
│                                  ▼                                         │
│                     ┌──────────────────┐                                   │
│                     │   Tool Execution │                                   │
│                     │   (if needed)    │                                   │
│                     └──────────────────┘                                   │
│                                  │                                         │
│                                  │ 2nd API call with tool results         │
│                                  ▼                                         │
│                        ┌──────────────────┐                               │
│                        │  Final Response  │                               │
│                        │   from Claude    │                               │
│                        └──────────────────┘                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                          │
                                          │ Return response & sources
                                          ▼
                               ┌──────────────────┐
                               │   Frontend       │
                               │   script.js:76   │
                               │                  │
                               │ Display response │
                               │ in chat UI       │
                               └──────────────────┘
```

## API Key Usage Summary

### Where the API Key is Used:
1. **Configuration**: Loaded from `.env` file via `ANTHROPIC_API_KEY` environment variable
2. **Client Setup**: Used to initialize Anthropic client in `ai_generator.py:33`
3. **API Calls**: Applied automatically to all Claude API calls through the client

### API Call Frequency:
- **1-2 calls per user query**:
  - **Primary call**: Initial query processing with system prompt and tools
  - **Follow-up call**: Only if tools were used, sends tool results for final response

### Security Notes:
- API key stored as environment variable (not in code)
- Loaded via `python-dotenv` from `.env` file
- Used through official Anthropic Python client library

## Key Files in Query Flow

| File | Purpose | API Key Involvement |
|------|---------|-------------------|
| `frontend/script.js` | User interface, API calls | ❌ None |
| `backend/app.py` | FastAPI endpoints | ❌ None |
| `backend/rag_system.py` | Query orchestration | ❌ None |
| `backend/config.py` | Configuration loading | 🔑 **Loads API key** |
| `backend/ai_generator.py` | Anthropic integration | 🔑 **Uses API key** |

## Model Configuration
- **Current Model**: `claude-3-5-haiku-20241022`
- **Temperature**: 0 (deterministic)
- **Max Tokens**: 800
- **System Prompt**: Course-specific instructions with tool usage guidelines