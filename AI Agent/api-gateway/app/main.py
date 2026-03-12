"""FastAPI application for the API Gateway."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.constants import API_TITLE, API_VERSION
from middleware.logging import LoggingMiddleware
from middleware.error_handler import ErrorHandlerMiddleware
from dependencies.rate_limit import limiter
from routers import chat_router

# Configure logging
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown."""
    logger.info(f"{API_TITLE} starting...")
    yield
    logger.info(f"{API_TITLE} shutting down...")


# Create FastAPI app
app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description="Restaurant Agent API Gateway",
    lifespan=lifespan
)

# Add rate limiter state
app.state.limiter = limiter

# Add middleware (order matters)
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
app.include_router(chat_router, prefix="/api/v1", tags=["Chat"])


# Health check endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": API_VERSION}


@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint."""
    return {"status": "ready"}


# Run the app
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
