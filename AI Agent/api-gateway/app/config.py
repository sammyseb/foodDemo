"""Configuration for the API Gateway."""

from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # App
    app_name: str = "Restaurant Agent API"
    version: str = "1.0.0"
    debug: bool = False
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # JWT
    jwt_secret: str = "change-this-secret-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 60
    
    # Rate Limiting
    rate_limit_per_minute: int = 60
    rate_limit_per_hour: int = 1000
    
    # CORS
    cors_origins: List[str] = Field(default_factory=lambda: ["http://localhost:3000", "http://localhost:5173"])
    
    # Agent Service
    agent_url: str = "http://localhost:8001"
    
    # MCP Server
    mcp_server_url: str = "http://localhost:8002"
    mcp_api_key: str = ""
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get application settings (cached)."""
    return Settings()


settings = get_settings()
