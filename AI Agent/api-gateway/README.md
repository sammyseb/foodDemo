# Restaurant Agent API Gateway

FastAPI-based API Gateway for the Restaurant Agent system.

## Overview

The API Gateway provides a unified entry point for the restaurant agent system with:
- JWT authentication
- Rate limiting
- Request/response transformation
- Error handling
- Logging

## Prerequisites

- Python 3.11+
- uv package manager

## Installation

```bash
# Install dependencies
cd api-gateway
uv sync

# Copy environment variables
cp .env.example .env

# Edit .env with your configuration
```

## Configuration

Create a `.env` file with the following variables:

| Variable | Description | Default |
|----------|--------------|---------|
| `JWT_SECRET` | Secret key for JWT tokens | (required) |
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8000` |
| `DEBUG` | Debug mode | `false` |
| `RATE_LIMIT_PER_MINUTE` | Requests per minute | `60` |
| `RATE_LIMIT_PER_HOUR` | Requests per hour | `1000` |
| `CORS_ORIGINS` | Allowed CORS origins | `http://localhost:3000` |
| `AGENT_URL` | Agent service URL | `http://localhost:8001` |
| `LOG_LEVEL` | Logging level | `INFO` |

## Running

### Development

```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Endpoints

### Authentication

#### POST /auth/login
Login and receive JWT token.

**Request:**
```json
{
  "username": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

### Chat

#### POST /chat
Send a chat message (requires authentication).

**Headers:**
```
Authorization: Bearer <token>
```

**Request:**
```json
{
  "message": "Find Italian restaurants in San Francisco",
  "session_id": "optional-session-id"
}
```

**Response:**
```json
{
  "message": "Here are some Italian restaurants...",
  "session_id": "abc-123",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### POST /chat/stream
Send a chat message with streaming response (requires authentication).

**Headers:**
```
Authorization: Bearer <token>
```

**Request:**
```json
{
  "message": "Find Italian restaurants in San Francisco",
  "session_id": "optional-session-id"
}
```

**Response:** Server-Sent Events stream

```
data: {"type": "start", "session_id": "abc-123"}
data: {"type": "content", "content": "Finding"}
data: {"type": "content", "content": " Italian restaurants..."}
data: {"type": "content", "content": " in San Francisco"}
data: {"type": "end"}
```

### Health

#### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "api-gateway"
}
```

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Web App   │────▶│ API Gateway │────▶│ LangGraph   │
│  (Client)   │     │  (FastAPI)  │     │   Agents    │
└─────────────┘     └─────────────┘     └─────────────┘
                          │
                    ┌─────┴─────┐
                    │  Auth &   │
                    │ Rate Limit│
                    └───────────┘
```

## Project Structure

```
api-gateway/
├── app/
│   ├── __init__.py
│   ├── config.py       # Configuration
│   ├── constants.py    # Constants
│   └── main.py         # FastAPI app
├── clients/
│   ├── __init__.py
│   └── agent_client.py # Agent service client
├── dependencies/
│   ├── __init__.py
│   ├── auth.py         # JWT authentication
│   └── rate_limit.py   # Rate limiting
├── middleware/
│   ├── __init__.py
│   ├── error_handler.py
│   └── logging.py
├── models/
│   ├── __init__.py
│   ├── request.py      # Request models
│   └── response.py     # Response models
├── routers/
│   ├── __init__.py
│   └── chat.py         # Chat endpoints
├── services/
│   ├── __init__.py
│   └── chat_service.py # Chat business logic
├── tests/
├── .env.example
├── pyproject.toml
└── README.md
```

## Integration with LangGraph Agents

The API Gateway communicates with the LangGraph Agent service:

1. **Non-streaming**: POST to `/agent/chat` 
2. **Streaming**: POST to `/agent/chat/stream`

Make sure the LangGraph Agent service is running (default: `http://localhost:8001`).

## Testing

```bash
# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov
```

## License

MIT
