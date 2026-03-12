"""Response models."""

from typing import Optional, List, Any
from pydantic import BaseModel


class ChatResponse(BaseModel):
    """Chat response."""
    message: str
    session_id: str
    intent: Optional[str] = None
    entities: Optional[dict] = None


class ErrorResponse(BaseModel):
    """Error response."""
    error: str
    message: str
    details: Optional[Any] = None


class SuccessResponse(BaseModel):
    """Generic success response."""
    message: str
    data: Optional[dict] = None
