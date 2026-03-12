"""Agent factory for creating configured agents."""

from typing import List, Optional

from langchain_openai import ChatOpenAI

from app.config import Settings, AgentConfig
from .router import RouterAgent
from .search import SearchAgent


class AgentFactory:
    """
    Factory for creating and configuring agents.
    
    This factory creates agents based on configuration and
    manages the lifecycle of LLM and tools.
    """
    
    def __init__(
        self, 
        settings: Settings, 
        config: Optional[AgentConfig] = None
    ):
        self.settings = settings
        self.config = config or AgentConfig()
        self._llm: Optional[ChatOpenAI] = None
        self._tools: List = []
    
    @property
    def llm(self) -> ChatOpenAI:
        """Get or create the LLM instance."""
        if self._llm is None:
            self._llm = ChatOpenAI(
                model=self.settings.openai_model,
                temperature=self.settings.openai_temperature,
                max_tokens=self.settings.openai_max_tokens,
                api_key=self.settings.openai_api_key or None
            )
        return self._llm
    
    @property
    def tools(self) -> List:
        """Get or create tools."""
        if not self._tools:
            from tools.factory import ToolFactory
            
            tool_factory = ToolFactory(
                mcp_server_url=self.settings.mcp_server_url,
                mcp_api_key=self.settings.mcp_api_key
            )
            self._tools = tool_factory.create_search_tools()
        
        return self._tools
    
    def create_router(self) -> RouterAgent:
        """Create the router agent."""
        return RouterAgent(self.llm)
    
    def create_search(self) -> SearchAgent:
        """Create the search agent with tools."""
        return SearchAgent(self.llm, self.tools)
    
    def create_all(self) -> dict:
        """Create all agents."""
        return {
            "router": self.create_router(),
            "search": self.create_search(),
        }


def create_agent_factory(settings: Optional[Settings] = None) -> AgentFactory:
    """Create an agent factory with default settings."""
    from app.config import get_settings
    
    if settings is None:
        settings = get_settings()
    
    return AgentFactory(settings)
