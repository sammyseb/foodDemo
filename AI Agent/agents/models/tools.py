"""Tool input models."""

from typing import Optional
from pydantic import BaseModel, Field


class SearchInput(BaseModel):
    """Input for restaurant search."""
    
    query: Optional[str] = Field(None, description="Search query text")
    location: Optional[str] = Field(None, description="City or neighborhood")
    cuisine: Optional[str] = Field(None, description="Cuisine type")
    price_range: Optional[str] = Field(None, description="Price range: $, $$, $$$$, $$$$$")
    rating_min: Optional[float] = Field(None, description="Minimum rating (0-5)", ge=0, le=5)
    radius: int = Field(5000, description="Search radius in meters", ge=100, le=50000)
    limit: int = Field(10, description="Maximum results to return", ge=1, le=50)


class RestaurantDetailInput(BaseModel):
    """Input for restaurant details."""
    
    place_id: str = Field(..., description="Google Places ID")
    fields: Optional[list[str]] = Field(
        None, 
        description="Fields to return"
    )


class ReviewInput(BaseModel):
    """Input for restaurant reviews."""
    
    place_id: str = Field(..., description="Google Places ID")
    limit: int = Field(20, description="Maximum reviews", ge=1, le=100)
