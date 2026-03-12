# Restaurant Agent API Gateway - Architecture

## Table of Contents

1. [Overview](#overview)
2. [Architecture Pattern](#architecture-pattern)
3. [Project Structure](#project-structure)
4. [Core Components](#core-components)
5. [Security](#security)
6. [API Endpoints](#api-endpoints)
7. [Middleware](#middleware)
8. [Integration](#integration)
9. [Deployment](#deployment)

---

## 1. Overview

The API Gateway is the central entry point for the Restaurant Agent system. It handles authentication, rate limiting, request validation, and routes requests to the appropriate backend services (LangGraph agents, MCP servers).

### 1.1 Responsibilities

| Responsibility | Description |
|---------------|-------------|
| **Authentication** | JWT-based auth, token validation |
| **Authorization** | Role-based access control |
| **Rate Limiting** | Per-user request limits |
| **Request Validation** | Pydantic models for all requests |
| **Routing** | Forward requests to agents/services |
| **Logging** | Structured request/response logging |
| **CORS** | Cross-origin request handling |
| **Streaming** | SSE support for real-time responses |

### 1.2 Tech Stack

| Component | Technology | Version |
|-----------|------------|---------|
| Framework | FastAPI | 0.109.x |
| Server | Uvicorn | 0.27.x |
| Auth | python-jose | 3.3.x |
| Validation | Pydantic | 2.x |
| Rate Limiting | SlowAPI | 0.9.x |
| Logging | Structlog | 24.x |
| CORS | FastAPI CORS | built-in |
| Testing | Pytest | 8.x |
| Type Checking | mypy | 1.x |

---

## 2. Architecture Pattern

### 2.1 Layered Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        ROUTERS                                   │
│  (FastAPI Routes - /chat, /restaurants, /reservations)          │
├─────────────────────────────────────────────────────────────────┤
│                        SERVICES                                  │
│  (Business Logic - ChatService, RestaurantService)              │
├─────────────────────────────────────────────────────────────────┤
│                        DEPENDENCIES                              │
│  (Auth, Rate Limiting, MCP Clients)                             │
├─────────────────────────────────────────────────────────────────┤
│                        EXTERNAL                                  │
│  (LangGraph Agents, MCP Server, Database)                       │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Request Flow

```
Client Request
      │
      ▼
┌─────────────────┐
│   CORS Middle  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Rate Limiter  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Auth Middleware│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Route Handler │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Agent/MCP    │
└────────┬────────┘
         │
         ▼
    Response
```

---

## 3. Project Structure

```
api-gateway/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Settings
│   └── constants.py            # Constants
├── routers/
│   ├── __init__.py
│   ├── chat.py                 # Chat endpoints
│   ├── restaurants.py          # Restaurant endpoints
│   ├── reservations.py        # Reservation endpoints
│   └── users.py                # User endpoints
├── services/
│   ├── __init__.py
│   ├── chat_service.py         # Chat business logic
│   ├── restaurant_service.py   # Restaurant business logic
│   └── agent_service.py        # Agent orchestration
├── dependencies/
│   ├── __init__.py
│   ├── auth.py                 # Auth dependencies
│   ├── rate_limit.py          # Rate limiting
│   └── mcp.py                  # MCP client management
├── models/
│   ├── __init__.py
│   ├── request.py              # Request models
│   ├── response.py             # Response models
│   └── domain.py               # Domain models
├── middleware/
│   ├── __init__.py
│   ├── logging.py              # Request logging
│   └── error_handler.py        # Error handling
├── clients/
│   ├── __init__.py
│   ├── mcp_client.py           # MCP HTTP client
│   └── agent_client.py         # LangGraph client
├── utils/
│   ├── __init__.py
│   ├── jwt_utils.py            # JWT helpers
│   └── validation.py           # Custom validators
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Pytest fixtures
│   ├── routers/
│   ├── services/
│   └── utils/
├── .env.example
├── pyproject.toml
├── uv.lock
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## 4. Core Components

### 4.1 Main Application

```python
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.middleware.logging import LoggingMiddleware
from app.middleware.error_handler import ErrorHandlerMiddleware
from routers import chat, restaurants, reservations, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("api_gateway_starting", version=settings.version)
    yield
    # Shutdown
    logger.info("api_gateway_shutting_down")


app = FastAPI(
    title="Restaurant Agent API",
    version=settings.version,
    description="AI-powered restaurant assistant API",
    lifespan=lifespan,
)

# Middleware (order matters - last added = first executed)
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(LoggingMiddleware)
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


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.version}


@app.get("/ready")
async def readiness_check():
    return {"status": "ready"}
```

### 4.2 Configuration

```python
# app/config.py
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
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # LangGraph Agent
    agent_url: str = "http://localhost:8001"
    
    # MCP Server
    mcp_server_url: str = "http://localhost:8002"
    mcp_api_key: str = ""
    
    # Database (optional)
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

### 4.3 Domain Models

```python
# models/domain.py
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum


class PriceRange(str, Enum):
    BUDGET = "$"
    MODERATE = "$$"
    UPSCALE = "$$$"
    FINE_DINING = "$$$$"


class Restaurant(BaseModel):
    id: str = Field(..., description="Unique restaurant identifier")
    name: str = Field(..., description="Restaurant name")
    address: Optional[str] = None
    vicinity: Optional[str] = None
    rating: Optional[float] = Field(None, ge=0, le=5)
    price_level: Optional[int] = Field(None, ge=1, le=4)
    photo_url: Optional[str] = None
    types: List[str] = []
    opening_hours: Optional[dict] = None
    website: Optional[str] = None
    phone: Optional[str] = None


class Review(BaseModel):
    id: str
    author_name: str
    rating: float = Field(..., ge=0, le=5)
    text: str
    time: int
    relative_time_description: Optional[str] = None


class User(BaseModel):
    id: str
    email: EmailStr
    name: str
    avatar: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Reservation(BaseModel):
    id: str
    restaurant_id: str
    restaurant_name: str
    user_id: str
    date: str
    time: str
    party_size: int = Field(..., ge=1)
    status: str = "pending"
    customer_name: str
    email: EmailStr
    phone: str
    special_requests: Optional[str] = None
    confirmation_code: str


class ChatMessage(BaseModel):
    id: str
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ChatSession(BaseModel):
    id: str
    user_id: str
    messages: List[ChatMessage] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

---

## 5. Security

### 5.1 JWT Authentication

```python
# dependencies/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from pydantic import BaseModel

from app.config import settings


security = HTTPBearer()


class TokenData(BaseModel):
    user_id: str
    email: str
    exp: int


class CurrentUser(BaseModel):
    id: str
    email: str
    name: str


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
        
        user_id: str = payload.get("sub")
        email: str = payload.get("email")
        
        if user_id is None or email is None:
            raise credentials_exception
            
        return CurrentUser(id=user_id, email=email, name=payload.get("name", ""))
        
    except JWTError:
        raise credentials_exception


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False))
) -> Optional[CurrentUser]:
    """Get user if authenticated, otherwise return None."""
    if credentials is None:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None
```

### 5.2 JWT Utilities

```python
# utils/jwt_utils.py
from datetime import datetime, timedelta
from jose import jwt
from app.config import settings


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expiration_minutes)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.jwt_secret, 
        algorithm=settings.jwt_algorithm
    )
    
    return encoded_jwt


def decode_token(token: str) -> dict:
    """Decode and validate JWT token."""
    return jwt.decode(
        token,
        settings.jwt_secret,
        algorithms=[settings.jwt_algorithm]
    )
```

### 5.3 Rate Limiting

```python
# dependencies/rate_limit.py
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse


limiter = Limiter(key_func=get_remote_address)


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Custom rate limit error handler."""
    return JSONResponse(
        status_code=429,
        content={
            "error": "Rate limit exceeded",
            "detail": f"Maximum {exc.detail} requests per hour",
            "retry_after": exc.detail
        }
    )


def get_user_rate_limit_key(request: Request) -> str:
    """Get rate limit key from user ID if authenticated."""
    # Will be implemented with auth
    return get_remote_address(request)
```

---

## 6. API Endpoints

### 6.1 Chat Endpoints

```python
# routers/chat.py
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional
import json

from dependencies.auth import get_current_user, CurrentUser
from dependencies.rate_limit import limiter
from services.chat_service import ChatService


router = APIRouter()


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    message: str
    session_id: str
    intent: Optional[str] = None
    entities: Optional[dict] = None


@router.post("/chat", response_model=ChatResponse)
@limiter.limit("60/minute")
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
    
    return result


@router.post("/chat/stream")
@limiter.limit("60/minute")
async def chat_stream(
    request: Request,
    chat_request: ChatRequest,
    current_user: CurrentUser = Depends(get_current_user)
):
    """Streaming chat endpoint with SSE."""
    service = ChatService()
    
    async def event_generator():
        # Send session ID
        session_id = chat_request.session_id or service.create_session_id()
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
            "X-Accel-Buffering": "no"
        }
    )


@router.get("/chat/sessions")
@limiter.limit("30/minute")
async def list_sessions(
    request: Request,
    current_user: CurrentUser = Depends(get_current_user)
):
    """List user's chat sessions."""
    service = ChatService()
    sessions = await service.get_user_sessions(current_user.id)
    return {"sessions": sessions}


@router.delete("/chat/sessions/{session_id}")
@limiter.limit("30/minute")
async def delete_session(
    request: Request,
    session_id: str,
    current_user: CurrentUser = Depends(get_current_user)
):
    """Delete a chat session."""
    service = ChatService()
    await service.delete_session(session_id, current_user.id)
    return {"message": "Session deleted"}
```

### 6.2 Restaurant Endpoints

```python
# routers/restaurants.py
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from typing import Optional, List

from dependencies.auth import get_current_user, CurrentUser
from dependencies.rate_limit import limiter
from services.restaurant_service import RestaurantService
from models.domain import Restaurant, Review


router = APIRouter()


class SearchParams(BaseModel):
    query: Optional[str] = None
    location: Optional[str] = None
    cuisine: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    radius: int = 5000
    limit: int = 10


class SearchResponse(BaseModel):
    results: List[Restaurant]
    total: int
    query: SearchParams


@router.get("/restaurants/search", response_model=SearchResponse)
@limiter.limit("120/minute")
async def search_restaurants(
    request: Request,
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
    
    return SearchResponse(
        results=results,
        total=len(results),
        query=SearchParams(
            query=query,
            location=location,
            cuisine=cuisine,
            lat=lat,
            lng=lng,
            radius=radius,
            limit=limit
        )
    )


@router.get("/restaurants/{place_id}", response_model=Restaurant)
@limiter.limit("60/minute")
async def get_restaurant(
    request: Request,
    place_id: str,
    current_user: CurrentUser = Depends(get_current_user)
):
    """Get restaurant details."""
    service = RestaurantService()
    restaurant = await service.get_by_id(place_id)
    
    if not restaurant:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    return restaurant


@router.get("/restaurants/{place_id}/reviews")
@limiter.limit("60/minute")
async def get_restaurant_reviews(
    request: Request,
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

## 7. Middleware

### 7.1 Logging Middleware

```python
# middleware/logging.py
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import structlog

logger = structlog.get_logger()


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Log request
        logger.info(
            "request_started",
            method=request.method,
            path=request.url.path,
            client_ip=request.client.host if request.client else None,
        )
        
        # Process request
        response = await call_next(request)
        
        # Log response
        logger.info(
            "request_completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
        )
        
        return response
```

### 7.2 Error Handler Middleware

```python
# middleware/error_handler.py
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
                    "message": str(exc) if request.app.debug else "An unexpected error occurred"
                }
            )
```

---

## 8. Integration

### 8.1 MCP Client

```python
# clients/mcp_client.py
from typing import AsyncIterator, Optional
import aiohttp
import json


class MCPClient:
    """Client for communicating with MCP servers."""
    
    def __init__(self, server_url: str, api_key: Optional[str] = None):
        self.server_url = server_url
        self.api_key = api_key
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self._session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            await self._session.close()
    
    async def call_tool(
        self, 
        tool_name: str, 
        arguments: dict
    ) -> AsyncIterator[dict]:
        """Call an MCP tool with streaming response."""
        if not self._session:
            self._session = aiohttp.ClientSession()
        
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        async with self._session.post(
            f"{self.server_url}/mcp/tools/call",
            json={
                "name": tool_name,
                "arguments": arguments
            },
            headers=headers
        ) as response:
            async for line in response.content:
                if line:
                    try:
                        data = json.loads(line)
                        yield data
                    except json.JSONDecodeError:
                        continue
    
    async def list_tools(self) -> list[dict]:
        """List available MCP tools."""
        if not self._session:
            self._session = aiohttp.ClientSession()
        
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        async with self._session.get(
            f"{self.server_url}/mcp/tools",
            headers=headers
        ) as response:
            data = await response.json()
            return data.get("tools", [])
```

### 8.2 Agent Client

```python
# clients/agent_client.py
from typing import AsyncIterator
import aiohttp
import json


class AgentClient:
    """Client for communicating with LangGraph agent service."""
    
    def __init__(self, agent_url: str):
        self.agent_url = agent_url
    
    async def chat(
        self,
        message: str,
        session_id: str,
        user_id: str
    ) -> AsyncIterator[dict]:
        """Send chat message to agent and stream response."""
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

## 9. Deployment

### 9.1 Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install uv for fast dependency management
RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 9.2 Docker Compose

```yaml
version: '3.8'

services:
  api-gateway:
    build: .
    ports:
      - "8000:8000"
    environment:
      - JWT_SECRET=${JWT_SECRET}
      - AGENT_URL=http://agent:8001
      - MCP_SERVER_URL=http://mcp:8002
    depends_on:
      - agent
      - mcp
    restart: unless-stopped

  agent:
    build: ../agents
    ports:
      - "8001:8001"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    restart: unless-stopped

  mcp:
    build: ../mcp-server
    ports:
      - "8002:8002"
    environment:
      - GOOGLE_PLACES_API_KEY=${GOOGLE_PLACES_API_KEY}
    restart: unless-stopped

networks:
  default:
    name: restaurant-agent-network
```

---

## Summary

The API Gateway provides:

| Feature | Implementation |
|---------|---------------|
| **Auth** | JWT with python-jose |
| **Rate Limiting** | SlowAPI |
| **Validation** | Pydantic models |
| **Routing** | FastAPI routers |
| **Streaming** | SSE for real-time |
| **Logging** | Structlog |
| **CORS** | FastAPI built-in |
| **Error Handling** | Custom middleware |
| **MCP Integration** | HTTP client |
| **Agent Integration** | Agent client |

---

## Next Steps

- See [Implementation Plan](./Implementation-Plan.md) for step-by-step guide
- Review [LangGraph Agent Architecture](../agents/Architecture.md)
- Set up [Development Environment](./SETUP.md)
