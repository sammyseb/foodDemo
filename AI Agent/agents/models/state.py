"""State definitions for LangGraph."""

from typing import TypedDict, Annotated, Optional, List, Any, Dict

from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """
    State managed by the LangGraph workflow.
    
    This state is passed through the graph and accumulates
    information as the agent processes the user's request.
    """
    
    # Messages (with automatic message addition via add_messages reducer)
    messages: Annotated[List[Any], add_messages]
    
    # Session information
    session_id: str
    user_id: str
    
    # Intent classification
    intent: Optional[str]
    entities: Optional[dict]
    
    # Current agent being used
    current_agent: str
    
    # Tool execution results
    tool_outputs: List[dict]
    
    # Final response to user
    final_response: str
    
    # Error handling
    error: Optional[str]
    retry_count: int


class SessionState(TypedDict):
    """Session state for maintaining conversation history."""
    
    session_id: str
    user_id: str
    created_at: float
    updated_at: float
    message_count: int
    context: Dict[str, Any]
