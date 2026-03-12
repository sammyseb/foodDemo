"""Response models."""

from typing import Optional, List, Any
from pydantic import BaseModel


class ChatResponse(BaseModel):
    """Response from chat endpoint."""
    
    message: str
    session_id: str
    intent: Optional[str] = None
    entities: Optional[dict] = None


class StreamChunk(BaseModel):
    """Streaming response chunk."""
    
    type: str  # "session_id", "content", "actions", "done", "error"
    session_id: Optional[str] = None
    text: Optional[str] = None
    actions: Optional[List[dict]] = None
    restaurants: Optional[List[Any]] = None
    error: Optional[str] = None
    intent: Optional[dict] = None


class ErrorResponse(BaseModel):
    """Error response."""
    
    error: str
    message: str
    details: Optional[dict] = None
