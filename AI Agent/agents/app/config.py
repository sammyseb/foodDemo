"""Configuration for the Restaurant Agent."""

from functools import lru_cache
from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # App
    app_name: str = "Restaurant Agent"
    version: str = "1.0.0"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8001
    
    # LLM - OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    openai_temperature: float = 0.7
    openai_max_tokens: int = 2000
    
    # MCP Server
    mcp_server_url: str = "http://localhost:8002"
    mcp_api_key: str = ""
    
    # Logging
    log_level: str = "INFO"
    
    # Debug
    debug: bool = False
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"


class AgentConfig(BaseModel):
    """Agent configuration model."""
    
    version: str = "1.0"
    llm: dict = {}
    agents: dict = {}
    tools: dict = {}
    intents: dict = {}
    
    @classmethod
    def from_yaml(cls, path: str = "config/agents.yaml") -> "AgentConfig":
        """Load configuration from YAML file."""
        config_path = Path(path)
        if config_path.exists():
            with open(config_path) as f:
                data = yaml.safe_load(f)
            return cls(**data) if data else cls()
        return cls()


def get_settings() -> Settings:
    """Get application settings (cached)."""
    return Settings()


@lru_cache()
def load_agent_config(path: str = "config/agents.yaml") -> AgentConfig:
    """Load agent configuration from YAML (cached)."""
    return AgentConfig.from_yaml(path)
