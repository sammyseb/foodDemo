"""Base agent class for all agents."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langgraph.prebuilt import ToolNode


class BaseAgent(ABC):
    """
    Base class for all agents in the Restaurant Agent system.
    
    This provides a common interface for:
    - Intent classification (router)
    - Restaurant search
    - Restaurant details
    - Reservations
    """
    
    def __init__(
        self,
        llm: BaseChatModel,
        tools: List[Any],
        system_prompt: str,
        max_iterations: int = 10
    ):
        self.llm = llm
        self.tools = tools
        self.system_prompt = system_prompt
        self.max_iterations = max_iterations
        self._tool_node: Optional[ToolNode] = None
    
    @abstractmethod
    async def ainvoke(
        self, 
        input_text: str, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process input and return result.
        
        Args:
            input_text: The user's input text
            context: Additional context including session info
            
        Returns:
            Dict with 'response' and optionally 'tool_outputs'
        """
        pass
    
    @abstractmethod
    async def astream(
        self, 
        input_text: str, 
        context: Dict[str, Any]
    ):
        """
        Process input and yield streaming results.
        
        Args:
            input_text: The user's input text
            context: Additional context including session info
            
        Yields:
            Stream chunks with type and data
        """
        pass
    
    @property
    def tool_node(self) -> ToolNode:
        """Get or create tool node for executing tools."""
        if self._tool_node is None and self.tools:
            self._tool_node = ToolNode(self.tools)
        return self._tool_node
    
    def _format_tools_description(self) -> str:
        """Format tools description for prompt."""
        if not self.tools:
            return "No tools available."
        
        descriptions = []
        for tool in self.tools:
            desc = getattr(tool, 'description', str(tool))
            name = getattr(tool, 'name', 'unknown')
            descriptions.append(f"- {name}: {desc}")
        
        return "\n".join(descriptions)
