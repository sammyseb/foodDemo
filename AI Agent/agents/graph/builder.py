"""Graph builder for LangGraph."""

from typing import Any, Dict

from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

from models.state import AgentState
from .nodes import (
    classify_intent,
    route_by_intent,
    execute_search,
    generate_response,
    handle_error,
)


class AgentGraph:
    """
    Manages the LangGraph workflow.
    
    This class builds and compiles the graph that orchestrates
    the flow from user message to final response.
    """
    
    def __init__(self, router_agent, search_agent, llm):
        self.router_agent = router_agent
        self.search_agent = search_agent
        self.llm = llm
        self._graph = None
    
    def build(self) -> StateGraph:
        """Build the LangGraph workflow."""
        
        graph = StateGraph(AgentState)
        
        # Add nodes
        graph.add_node("classify_intent", classify_intent)
        graph.add_node("search_agent", execute_search)
        graph.add_node("generate_response", generate_response)
        graph.add_node("handle_error", handle_error)
        
        # Set entry point
        graph.set_entry_point("classify_intent")
        
        # Route to appropriate agent
        graph.add_edge("classify_intent", "route_by_intent")
        
        # Conditional routing based on intent
        graph.add_conditional_edges(
            "route_by_intent",
            route_by_intent,
            {
                "search_agent": "search_agent",
                "generate_response": "generate_response"
            }
        )
        
        # All agents lead to response generation
        graph.add_edge("search_agent", "generate_response")
        
        # Handle errors
        graph.add_edge("generate_response", END)
        
        return graph.compile()
    
    @property
    def graph(self):
        """Get or build the compiled graph."""
        if self._graph is None:
            self._graph = self.build()
        return self._graph
    
    async def ainvoke(self, initial_state: Dict[str, Any]) -> Dict[str, Any]:
        """Invoke the graph."""
        return await self.graph.ainvoke(initial_state)
    
    async def astream(self, initial_state: Dict[str, Any]):
        """Stream the graph execution."""
        async for chunk in self.graph.astream(initial_state):
            yield chunk


def create_agent_graph(router_agent, search_agent, llm) -> StateGraph:
    """
    Create the LangGraph workflow.
    
    Args:
        router_agent: The router agent for intent classification
        search_agent: The search agent for restaurant search
        llm: The language model
        
    Returns:
        Compiled LangGraph
    """
    builder = AgentGraph(router_agent, search_agent, llm)
    return builder.graph


def create_initial_state(
    message: str,
    session_id: str,
    user_id: str,
    router_agent,
    search_agent,
    llm
) -> AgentState:
    """
    Create initial state for the graph.
    
    Args:
        message: The user's message
        session_id: The session ID
        user_id: The user ID
        router_agent: Router agent instance
        search_agent: Search agent instance
        llm: Language model instance
        
    Returns:
        Initial state dict
    """
    from langchain_core.messages import HumanMessage
    
    return {
        "messages": [HumanMessage(content=message)],
        "session_id": session_id,
        "user_id": user_id,
        "intent": None,
        "entities": {},
        "current_agent": "router",
        "tool_outputs": [],
        "final_response": "",
        "error": None,
        "retry_count": 0,
        "router_agent": router_agent,
        "search_agent": search_agent,
        "llm": llm
    }
