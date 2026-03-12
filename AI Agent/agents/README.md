# Restaurant Agent - LangGraph Orchestration Layer

<p align="center">
  <img src="https://img.shields.io/badge/LangGraph-0.2.x-blue" alt="LangGraph">
  <img src="https://img.shields.io/badge/LangChain-0.3.x-blue" alt="LangChain">
  <img src="https://img.shields.io/badge/Python-3.11+-green" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-0.109+-green" alt="FastAPI">
</p>

An AI-powered restaurant assistant built with LangGraph for orchestrating multi-agent workflows. This service handles intent classification, entity extraction, and restaurant search using OpenAI's GPT models.

## Table of Contents

- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Agent](#running-the-agent)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)
- [Project Structure](#project-structure)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     RESTAURANT AGENT                              │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   LangGraph Workflow                      │   │
│  │                                                          │   │
│  │  User Message                                            │   │
│  │       │                                                  │   │
│  │       ▼                                                  │   │
│  │  ┌──────────────────┐                                    │   │
│  │  │ Intent Router   │──── Intent Classification           │   │
│  │  └────────┬─────────┘                                    │   │
│  │           │                                               │   │
│  │           ▼                                               │   │
│  │  ┌──────────────────┐                                    │   │
│  │  │  Entity Extract  │──── Location, Cuisine, Date        │   │
│  │  └────────┬─────────┘                                    │   │
│  │           │                                               │   │
│  │           ▼                                               │   │
│  │  ┌──────────────────┐                                    │   │
│  │  │  Search Agent    │──── Restaurant Search (MCP Tools)  │   │
│  │  └────────┬─────────┘                                    │   │
│  │           │                                               │   │
│  │           ▼                                               │   │
│  │  ┌──────────────────┐                                    │   │
│  │  │ Response Generate│──── Friendly Response              │   │
│  │  └──────────────────┘                                    │   │
│  │                                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌────────────────┐   │
│  │   Router Agent │  │  Search Agent  │  │  LLM (GPT-4o)  │   │
│  └─────────────────┘  └─────────────────┘  └────────────────┘   │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    MCP Tools                                │ │
│  │  • search_restaurants   • get_restaurant_details         │ │
│  │  • get_restaurant_reviews                                 │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## Quick Start

### 1. Clone and Install

```bash
cd agents

# Install uv if you don't have it
pip install uv

# Install dependencies
uv sync
```

### 2. Configure

```bash
# Copy environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
nano .env
```

### 3. Run

```bash
# Run the server
uvicorn app.main:app --reload --port 8001
```

### 4. Test

```bash
# Test the health endpoint
curl http://localhost:8001/health

# Test chat (non-streaming)
curl -X POST http://localhost:8001/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Find Italian restaurants in San Francisco"}'

# Test chat (streaming)
curl -X POST http://localhost:8001/agent/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "Find Japanese restaurants near me"}'
```

---

## Prerequisites

| Requirement | Version | Description |
|-------------|---------|-------------|
| Python | 3.11+ | Runtime |
| uv | Latest | Package manager |
| OpenAI API Key | - | For GPT-4o access |
| MCP Server | Optional | For real restaurant data |

### Getting an OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in
3. Navigate to API Keys
4. Create a new secret key
5. Copy it to your `.env` file

---

## Installation

### Using uv (Recommended)

```bash
# Install uv if needed
pip install uv

# Sync dependencies
uv sync

# Install dev dependencies
uv sync --dev
```

### Using pip

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
```

---

## Configuration

### Environment Variables

Create a `.env` file in the `agents` directory:

```bash
# Required
OPENAI_API_KEY=sk-your-api-key-here

# MCP Server (Optional - for real restaurant data)
MCP_SERVER_URL=http://localhost:8002
MCP_API_KEY=

# Server
HOST=0.0.0.0
PORT=8001
DEBUG=false

# LLM Settings
OPENAI_MODEL=gpt-4o
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=2000

# Logging
LOG_LEVEL=INFO
```

### Configuration File

You can also customize agent behavior in `config/agents.yaml`:

```yaml
version: "1.0"

llm:
  provider: "openai"
  model: "gpt-4o"
  temperature: 0.7
  max_tokens: 2000

agents:
  router:
    description: "Routes user requests"
    max_iterations: 3

  search:
    description: "Searches for restaurants"
    max_iterations: 10

tools:
  search_restaurants:
    mcp_server: "google_places"
    mcp_tool: "search_restaurants"
    default_radius: 5000
    max_results: 10
```

---

## Running the Agent

### Development Mode

```bash
# Run with auto-reload
uvicorn app.main:app --reload --port 8001

# Or use the run script
python -m app.main
```

### Production Mode

```bash
# Run with multiple workers
uvicorn app.main:app --host 0.0.0.0 --port 8001 --workers 4

# Or use gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Docker

```bash
# Build the image
docker build -t restaurant-agent .

# Run the container
docker run -p 8001:8001 \
  -e OPENAI_API_KEY=your-key \
  restaurant-agent
```

---

## API Endpoints

### Health Check

```bash
GET /health
```

Response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "service": "restaurant-agent"
}
```

### Chat (Non-Streaming)

```bash
POST /agent/chat
```

Request:
```json
{
  "message": "Find Italian restaurants in San Francisco",
  "session_id": "optional-session-id",
  "user_id": "optional-user-id"
}
```

Response:
```json
{
  "message": "I've found some great Italian restaurants in San Francisco!",
  "session_id": "abc-123",
  "intent": "search",
  "entities": {
    "location": "San Francisco",
    "cuisine": "Italian"
  }
}
```

### Chat (Streaming)

```bash
POST /agent/chat/stream
```

Response format (SSE):
```
data: {"type": "session_id", "session_id": "abc-123"}
data: {"type": "intent", "data": {"intent": "search", "entities": {"location": "SF"}}}
data: {"type": "content", "text": "I've found some great Italian restaurants..."}
data: {"type": "actions", "data": [...]}
data: [DONE]
```

---

## Testing

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test file
pytest tests/test_agents.py -v
```

### Example Test

```python
import pytest
from agents.factory import AgentFactory
from app.config import Settings

def test_agent_factory():
    settings = Settings(openai_api_key="test-key")
    factory = AgentFactory(settings)
    
    router = factory.create_router()
    assert router is not None
    
    search = factory.create_search()
    assert search is not None
```

---

## Project Structure

```
agents/
├── app/
│   ├── __init__.py
│   ├── config.py          # Settings and configuration
│   ├── constants.py       # Constants
│   └── main.py            # FastAPI application
├── agents/
│   ├── __init__.py
│   ├── base.py            # Base agent class
│   ├── router.py          # Intent router agent
│   ├── search.py          # Restaurant search agent
│   └── factory.py         # Agent factory
├── graph/
│   ├── __init__.py
│   ├── nodes.py           # Graph nodes
│   └── builder.py         # Graph builder
├── tools/
│   ├── __init__.py
│   ├── mcp_wrapper.py     # MCP tool wrapper
│   └── factory.py         # Tool factory
├── models/
│   ├── __init__.py
│   ├── state.py           # Agent state
│   ├── tools.py           # Tool models
│   └── responses.py       # Response models
├── config/
│   └── agents.yaml        # Agent configuration
├── tests/
│   └── ...
├── pyproject.toml
├── .env.example
└── README.md
```

---

## Key Features

### 1. Intent Classification
The router agent analyzes user messages to determine their intent:
- `search`: Looking for restaurants
- `details`: Want specific info
- `reserve`: Making reservations
- `chat`: General conversation

### 2. Entity Extraction
Automatically extracts:
- Location (city, neighborhood)
- Cuisine type
- Price range
- Rating preferences
- Date and time

### 3. Tool Integration
Connects to MCP servers for:
- Restaurant search
- Restaurant details
- Reviews

### 4. Streaming Support
Real-time responses via Server-Sent Events (SSE)

---

## Troubleshooting

### OpenAI API Key Error

If you see an authentication error:
1. Check your `.env` file has the correct API key
2. Verify the key has credits available
3. Check API key format (should start with `sk-`)

### Import Errors

If you get import errors:
```bash
# Reinstall dependencies
uv sync --force-reinstall
```

### MCP Connection Error

If MCP server is not running:
```bash
# The agent will use mock data by default
# Or start your MCP server on port 8002
```

---

## License

MIT License - See LICENSE file for details.

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request
