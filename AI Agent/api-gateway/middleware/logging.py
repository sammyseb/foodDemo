"""Logging middleware."""

import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Request/response logging middleware."""
    
    async def dispatch(self, request: Request, call_next):
        # Skip health checks
        if request.url.path in ["/health", "/ready"]:
            return await call_next(request)
        
        # Log request
        logger.info(
            f"{request.method} {request.url.path}",
            method=request.method,
            path=request.url.path,
            client=request.client.host if request.client else None,
        )
        
        response = await call_next(request)
        
        # Log response
        logger.info(
            f"{request.method} {request.url.path} - {response.status_code}",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
        )
        
        return response
