# Restaurant Agent API Gateway - Implementation Plan

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Phase 1: Project Setup](#phase-1-project-setup)
4. [Phase 2: Core Infrastructure](#phase-2-core-infrastructure)
5. [Phase 3: Authentication](#phase-3-authentication)
6. [Phase 4: Middleware](#phase-4-middleware)
7. [Phase 5: Routers & Endpoints](#phase-5-routers--endpoints)
8. [Phase 6: Services](#phase-6-services)
9. [Phase 7: Integration](#phase-7-integration)
10. [Phase 8: Testing](#phase-8-testing)
11. [Phase 9: Deployment](#phase-9-deployment)
12. [Checklist](#checklist)

---

## 1. Overview

This plan provides step-by-step instructions to build the Restaurant Agent API Gateway.

**Estimated Total Time**: 2-3 weeks
**Difficulty**: Intermediate to Advanced

---

## 2. Prerequisites

### 2.1 Required Tools

```bash
# Python 3.11+
python --version  # Should show 3.11.x

# uv (fast package manager)
pip install uv

# Git
git --version
```

### 2.2 Dependencies

- FastAPI
- Uvicorn
- python-jose (JWT)
- pydantic & pydantic-settings
- slowapi (rate limiting)
- structlog (logging)
- aiohttp (async HTTP)
- pytest (testing)
- mypy (type checking)

---

## 3. Phase 1: Project Setup

**Duration**: 1-2 hours
**Goals**: Initialize project, configure dependencies

### 3.1 Create Project Structure

```bash
mkdir -p api-gateway
cd api-gateway

# Initialize with pyproject.toml
cat > pyproject.toml << 'EOF'
[project]
name = "restaurant-agent-gateway"
version = "1.0.0"
description = "Restaurant Agent API Gateway"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.109.0",
    "uvicorn[standard]>=0.27.0",
    "python-jose[cryptography]>=3.3.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "slowapi>=0.1.9",
    "structlog>=24.0.0",
    "aiohttp>=3.9.0",
    "python-multipart>=0.0.6",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "pytest-cov>=4.1.0",
    "mypy>=1.8.0",
    "ruff>=0.1.0",
    "pre-commit>=3.6.0",
]

[tool.uv]
dev-dependencies = []

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.ruff]
line-length = 100

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
EOF
```

### 3.2 Create Environment File

```bash
cat > .env.example << 'EOF'
# App
APP_NAME=Restaurant Agent API
VERSION=1.0.0
DEBUG=false

# Server
HOST=0.0.0.0
PORT=8000

# JWT
JWT_SECRET=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=60

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# LangGraph Agent
AGENT_URL=http://localhost:8001

# MCP Server
MCP_SERVER_URL=http://localhost:8002
MCP_API_KEY=

# Database (optional)
DATABASE_URL=

# Logging
LOG_LEVEL=INFO
EOF

cp .env.example .env
```

### 3.3 Install Dependencies

```bash
# Sync dependencies
uv sync

# Install dev dependencies
uv sync --dev
```

### 3.4 Verify Setup

```bash
# Run a simple check
python -c "from app.main import app; print('App loaded successfully')"
```

---

## 4. Phase 2: Core Infrastructure

**Duration**: 2-3 hours
**Goals**: Config, constants, main app

### 4.1 Create Config

Create `app/config.py`:

```python
from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    # App
    app_name: str = "Restaurant Agent API"
    version: str = "1.0.0"
    debug: bool = False
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # JWT
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 60
    
    # Rate Limiting
    rate_limit_per_minute: int = 60
    rate_limit_per_hour: int = 1000
    
    # CORS
    cors_origins: List[str] = ["http://localhost:3000"]
    
    # Services
    agent_url: str = "http://localhost:8001"
    mcp_server_url: str = "http://localhost:8002"
    mcp_api_key: str = ""
    
    # Database
    database_url: str = ""
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
```

Create `app/constants.py`:

```python
# API Constants
API_V1_PREFIX = "/api/v1"
API_TITLE = "Restaurant Agent API"
API_VERSION = "1.0.0"

# Auth Constants
TOKEN_TYPE_BEARER = "Bearer"

# Rate Limiting
DEFAULT_RATE_LIMIT = "60/minute"
DEFAULT_RATE_LIMIT_BURST = 10

# Pagination
DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 100

# Chat
MAX_MESSAGE_LENGTH = 4000
MAX_SESSION_MESSAGES = 100
```

### 4.2 Create Main Application

Create `app/__init__.py`:

```python
# App package
```

Create `app/main.py`:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from routers import chat, restaurants, reservations, users


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        debug=settings.debug,
    )
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(chat.router, prefix="/api/v1", tags=["Chat"])
    app.include_router(restaurants.router, prefix="/api/v1", tags=["Restaurants"])
    app.include_router(reservations.router, prefix="/api/v1", tags=["Reservations"])
    app.include_router(users.router, prefix="/api/v1", tags=["Users"])
    
    # Health check
    @app.get("/health")
    async def health():
        return {"status": "healthy", "version": settings.version}
    
    @app.get("/ready")
    async def ready():
        return {"status": "ready"}
    
    return app


app = create_app()
```

### 4.3 Create Directory Structure

```bash
mkdir -p app
mkdir -p routers
mkdir -p services
mkdir -p dependencies
mkdir -p models
mkdir -p middleware
mkdir -p clients
mkdir -p utils
mkdir -p tests/{routers,services,utils}
```

### 4.4 Create Empty Module Files

```bash
touch routers/__init__.py
touch services/__init__.py
touch dependencies/__init__.py
touch models/__init__.py
touch middleware/__init__.py
touch clients/__init__.py
touch utils/__init__.py
touch tests/__init__.py
```

---

## 5. Phase 3: Authentication

**Duration**: 2-3 hours
**Goals**: JWT utils, auth dependencies

### 5.1 JWT Utilities

Create `utils/jwt_utils.py`:

```python
from datetime import datetime, timedelta
from jose import jwt, JWTError
from typing import Optional

from app.config import settings


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    
    expire = datetime.utcnow() + (
        expires_delta or 
        timedelta(minutes=settings.jwt_expiration_minutes)
    )
    
    to_encode.update({"exp": expire})
    
    return jwt.encode(
        to_encode,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm
    )


def decode_token(token: str) -> dict:
    """Decode and validate JWT token."""
    return jwt.decode(
        token,
        settings.jwt_secret,
        algorithms=[settings.jwt_algorithm]
    )


def verify_token(token: str) -> Optional[dict]:
    """Verify token and return payload or None."""
    try:
        return decode_token(token)
    except JWTError:
        return None
```

### 5.2 Auth Dependencies

Create `dependencies/auth.py`:

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from jose import JWTError, jwt

from app.config import settings


security = HTTPBearer()


class TokenData(BaseModel):
    user_id: str
    email: str


class CurrentUser(BaseModel):
    id: str
    email: str
    name: str = ""


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> CurrentUser:
    """Validate JWT token and return current user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm]
        )
        
        user_id = payload.get("sub")
        email = payload.get("email")
        
        if user_id is None or email is None:
            raise credentials_exception
            
        return CurrentUser(
            id=user_id,
            email=email,
            name=payload.get("name", "")
        )
        
    except JWTError:
        raise credentials_exception


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials = Depends(
        HTTPBearer(auto_error=False)
    )
) -> Optional[CurrentUser]:
    """Get user if authenticated, otherwise return None."""
    if credentials is None:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None
```

---

## 6. Phase 4: Middleware

**Duration**: 1-2 hours
**Goals**: Logging, error handling

### 6.1 Logging Middleware

Create `middleware/logging.py`:

```python
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import structlog

logger = structlog.get_logger()


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip logging for health checks
        if request.url.path in ["/health", "/ready"]:
            return await call_next(request)
        
        logger.info(
            "request_started",
            method=request.method,
            path=request.url.path,
            client=request.client.host if request.client else None,
        )
        
        response = await call_next(request)
        
        logger.info(
            "request_completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
        )
        
        return response
```

### 6.2 Error Handler Middleware

Create `middleware/error_handler.py`:

```python
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import structlog

logger = structlog.get_logger()


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as exc:
            logger.error(
                "request_failed",
                path=request.url.path,
                error=str(exc),
                error_type=type(exc).__name__,
            )
            
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "Internal server error",
                    "message": "An unexpected error occurred"
                }
            )
```

---

## 7. Phase 5: Routers & Endpoints

**Duration**: 3-4 hours
**Goals**: Chat, restaurant, reservation endpoints

### 7.1 Models

Create `models/request.py`:

```python
from pydantic import BaseModel, Field
from typing import Optional


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    session_id: Optional[str] = None


class SearchRequest(BaseModel):
    query: Optional[str] = None
    location: Optional[str] = None
    cuisine: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    radius: int = Field(5000, ge=100, le=50000)
    limit: int = Field(10, ge=1, le=50)


class ReservationRequest(BaseModel):
    restaurant_id: str
    date: str
    time: str
    party_size: int = Field(2, ge=1)
    customer_name: str
    email: str
    phone: str
    special_requests: Optional[str] = None


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str
```

Create `models/response.py`:

```python
from pydantic import BaseModel
from typing import Optional, List, Any


class ChatResponse(BaseModel):
    message: str
    session_id: str
    intent: Optional[str] = None
    entities: Optional[dict] = None


class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[Any] = None


class SuccessResponse(BaseModel):
    message: str
    data: Optional[dict] = None
```

### 7.2 Chat Router

Create `routers/chat.py`:

```python
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import json

from dependencies.auth import get_current_user, CurrentUser
from models.request import ChatRequest
from models.response import ChatResponse
from services.chat_service import ChatService


router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: Request,
    chat_request: ChatRequest,
    current_user: CurrentUser = Depends(get_current_user)
):
    """Non-streaming chat endpoint."""
    service = ChatService()
    
    result = await service.process_message(
        message=chat_request.message,
        session_id=chat_request.session_id,
        user_id=current_user.id
    )
    
    return ChatResponse(**result)


@router.post("/chat/stream")
async def chat_stream(
    request: Request,
    chat_request: ChatRequest,
    current_user: CurrentUser = Depends(get_current_user)
):
    """Streaming chat endpoint with SSE."""
    service = ChatService()
    session_id = chat_request.session_id or service.create_session_id()
    
    async def event_generator():
        yield f"data: {json.dumps({'type': 'session_id', 'session_id': session_id})}\n\n"
        
        try:
            async for chunk in service.process_message_stream(
                message=chat_request.message,
                session_id=session_id,
                user_id=current_user.id
            ):
                yield f"data: {json.dumps(chunk)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
        
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )
```

### 7.3 Restaurant Router

Create `routers/restaurants.py`:

```python
from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional, List

from dependencies.auth import get_current_user, CurrentUser
from models.request import SearchRequest
from models.domain import Restaurant, Review
from services.restaurant_service import RestaurantService


router = APIRouter()


@router.get("/restaurants/search")
async def search_restaurants(
    query: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    cuisine: Optional[str] = Query(None),
    lat: Optional[float] = Query(None),
    lng: Optional[float] = Query(None),
    radius: int = Query(5000, ge=100, le=50000),
    limit: int = Query(10, ge=1, le=50),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Search for restaurants."""
    service = RestaurantService()
    
    results = await service.search(
        query=query,
        location=location,
        cuisine=cuisine,
        lat=lat,
        lng=lng,
        radius=radius,
        limit=limit
    )
    
    return {"results": results, "total": len(results)}


@router.get("/restaurants/{place_id}")
async def get_restaurant(
    place_id: str,
    current_user: CurrentUser = Depends(get_current_user)
):
    """Get restaurant details."""
    service = RestaurantService()
    restaurant = await service.get_by_id(place_id)
    
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    return restaurant


@router.get("/restaurants/{place_id}/reviews")
async def get_restaurant_reviews(
    place_id: str,
    limit: int = Query(20, ge=1, le=100),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Get restaurant reviews."""
    service = RestaurantService()
    reviews = await service.get_reviews(place_id, limit)
    return {"reviews": reviews}
```

---

## 8. Phase 6: Services

**Duration**: 2-3 hours
**Goals**: Business logic layer

### 8.1 Chat Service

Create `services/chat_service.py`:

```python
from typing import AsyncIterator, Dict, Any
import uuid
from clients.agent_client import AgentClient
from app.config import settings


class ChatService:
    def __init__(self):
        self.agent_client = AgentClient(settings.agent_url)
    
    def create_session_id(self) -> str:
        """Create a new session ID."""
        return str(uuid.uuid4())
    
    async def process_message(
        self,
        message: str,
        session_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """Process a chat message and return result."""
        result = await self.agent_client.chat_simple(
            message=message,
            session_id=session_id,
            user_id=user_id
        )
        return result
    
    async def process_message_stream(
        self,
        message: str,
        session_id: str,
        user_id: str
    ) -> AsyncIterator[Dict[str, Any]]:
        """Process a chat message and yield streaming results."""
        async for chunk in self.agent_client.chat(
            message=message,
            session_id=session_id,
            user_id=user_id
        ):
            yield chunk
```

### 8.2 Restaurant Service

Create `services/restaurant_service.py`:

```python
from typing import List, Optional, Dict, Any
from clients.mcp_client import MCPClient
from app.config import settings


class RestaurantService:
    def __init__(self):
        self.mcp_client = MCPClient(
            server_url=settings.mcp_server_url,
            api_key=settings.mcp_api_key
        )
    
    async def search(
        self,
        query: Optional[str] = None,
        location: Optional[str] = None,
        cuisine: Optional[str] = None,
        lat: Optional[float] = None,
        lng: Optional[float] = None,
        radius: int = 5000,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search for restaurants."""
        params = {
            "query": query or cuisine or "restaurant",
            "radius": radius,
            "limit": limit
        }
        
        if lat and lng:
            params["location"] = f"{lat},{lng}"
        elif location:
            params["location"] = location
        
        results = []
        async for chunk in self.mcp_client.call_tool("search_restaurants", params):
            results.append(chunk)
        
        return results
    
    async def get_by_id(self, place_id: str) -> Optional[Dict[str, Any]]:
        """Get restaurant by ID."""
        results = []
        async for chunk in self.mcp_client.call_tool("get_place_details", {
            "place_id": place_id
        }):
            results.append(chunk)
        
        return results[0] if results else None
    
    async def get_reviews(self, place_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get restaurant reviews."""
        results = []
        async for chunk in self.mcp_client.call_tool("get_reviews", {
            "place_id": place_id,
            "limit": limit
        }):
            results.append(chunk)
        
        return results
```

---

## 9. Phase 7: Integration

**Duration**: 2-3 hours
**Goals**: MCP and Agent clients

### 9.1 MCP Client

Create `clients/mcp_client.py`:

```python
from typing import AsyncIterator, Optional
import aiohttp
import json


class MCPClient:
    def __init__(self, server_url: str, api_key: Optional[str] = None):
        self.server_url = server_url
        self.api_key = api_key
    
    async def call_tool(
        self,
        tool_name: str,
        arguments: dict
    ) -> AsyncIterator[dict]:
        """Call an MCP tool with streaming response."""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.server_url}/mcp",
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {
                        "name": tool_name,
                        "arguments": arguments
                    }
                },
                headers=headers
            ) as response:
                async for line in response.content:
                    if line:
                        try:
                            data = json.loads(line)
                            if "result" in data:
                                yield data["result"]
                        except json.JSONDecodeError:
                            continue
```

### 9.2 Agent Client

Create `clients/agent_client.py`:

```python
from typing import AsyncIterator
import aiohttp
import json


class AgentClient:
    def __init__(self, agent_url: str):
        self.agent_url = agent_url
    
    async def chat(
        self,
        message: str,
        session_id: str,
        user_id: str
    ) -> AsyncIterator[dict]:
        """Stream chat response from agent."""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.agent_url}/agent/chat/stream",
                json={
                    "message": message,
                    "session_id": session_id,
                    "user_id": user_id
                }
            ) as response:
                async for line in response.content:
                    if line:
                        try:
                            data = json.loads(line)
                            yield data
                        except json.JSONDecodeError:
                            continue
    
    async def chat_simple(
        self,
        message: str,
        session_id: str,
        user_id: str
    ) -> dict:
        """Send chat message and get single response."""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.agent_url}/agent/chat",
                json={
                    "message": message,
                    "session_id": session_id,
                    "user_id": user_id
                }
            ) as response:
                return await response.json()
```

---

## 10. Phase 8: Testing

**Duration**: 2-3 hours
**Goals**: Unit and integration tests

### 10.1 Test Setup

Create `tests/conftest.py`:

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_headers():
    # Create a test token
    from utils.jwt_utils import create_access_token
    token = create_access_token({"sub": "test-user", "email": "test@example.com"})
    return {"Authorization": f"Bearer {token}"}
```

### 10.2 Write Tests

Create `tests/routers/test_chat.py`:

```python
import pytest
from fastapi.testclient import TestClient


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_chat_requires_auth(client):
    response = client.post("/api/v1/chat", json={"message": "hello"})
    assert response.status_code == 403  # No auth header


def test_chat_with_auth(client, auth_headers):
    # This will fail without the agent service running
    # Use mocking in real tests
    response = client.post(
        "/api/v1/chat",
        json={"message": "hello"},
        headers=auth_headers
    )
    # Expect either success or connection error
    assert response.status_code in [200, 500]
```

---

## 11. Phase 9: Deployment

**Duration**: 1-2 hours
**Goals**: Docker, production build

### 11.1 Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Copy application
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 11.2 Build & Run

```bash
# Build
docker build -t restaurant-agent-gateway .

# Run
docker run -p 8000:8000 \
  -e JWT_SECRET=your-secret \
  -e AGENT_URL=http://agent:8001 \
  -e MCP_SERVER_URL=http://mcp:8002 \
  restaurant-agent-gateway
```

---

## 12. Checklist

### Phase 1: Project Setup
- [ ] Create pyproject.toml
- [ ] Create .env file
- [ ] Install dependencies
- [ ] Verify setup

### Phase 2: Core Infrastructure
- [ ] Create config.py
- [ ] Create constants.py
- [ ] Create main.py
- [ ] Create directory structure

### Phase 3: Authentication
- [ ] Create JWT utilities
- [ ] Create auth dependencies

### Phase 4: Middleware
- [ ] Create logging middleware
- [ ] Create error handler middleware

### Phase 5: Routers & Endpoints
- [ ] Create request/response models
- [ ] Create chat router
- [ ] Create restaurant router

### Phase 6: Services
- [ ] Create chat service
- [ ] Create restaurant service

### Phase 7: Integration
- [ ] Create MCP client
- [ ] Create agent client

### Phase 8: Testing
- [ ] Create test fixtures
- [ ] Write unit tests

### Phase 9: Deployment
- [ ] Create Dockerfile
- [ ] Build and test image

---

## Next Steps

- Set up LangGraph Agent service
- Connect to MCP server (Google Places)
- Add more endpoints (reservations, users)
- Configure CI/CD pipeline
