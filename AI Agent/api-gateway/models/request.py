"""Request models."""

from typing import Optional
from pydantic import BaseModel, Field, EmailStr


class ChatRequest(BaseModel):
    """Chat request model."""
    message: str = Field(..., min_length=1, max_length=4000)
    session_id: Optional[str] = None


class SearchRequest(BaseModel):
    """Restaurant search request."""
    query: Optional[str] = None
    location: Optional[str] = None
    cuisine: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    radius: int = Field(5000, ge=100, le=50000)
    limit: int = Field(10, ge=1, le=50)


class ReservationRequest(BaseModel):
    """Reservation request."""
    restaurant_id: str
    date: str
    time: str
    party_size: int = Field(2, ge=1)
    customer_name: str
    email: EmailStr
    phone: str
    special_requests: Optional[str] = None


class LoginRequest(BaseModel):
    """Login request."""
    email: str
    password: str


class RegisterRequest(BaseModel):
    """Registration request."""
    email: EmailStr
    password: str
    name: str
