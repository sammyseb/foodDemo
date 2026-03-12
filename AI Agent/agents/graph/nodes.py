"""Graph nodes for LangGraph orchestration."""

from typing import Any, Dict

from langchain_core.messages import HumanMessage, AIMessage

from app.constants import INTENT_MAPPING


async def classify_intent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Classify user intent using the router agent.
    
    This is the entry point for the graph. It takes the user's
    message and determines what they want to do.
    """
    messages = state["messages"]
    last_message = messages[-1].content if messages else ""
    
    router_agent = state["router_agent"]
    result = await router_agent.ainvoke(last_message, state)
    
    return {
        **state,
        "intent": result.get("intent", "chat"),
        "entities": result.get("entities", {})
    }


def route_by_intent(state: Dict[str, Any]) -> str:
    """
    Route to the appropriate agent based on intent.
    
    Maps the detected intent to an agent name.
    """
    intent = state.get("intent", "chat")
    
    return INTENT_MAPPING.get(intent, "generate_response")


async def execute_search(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute the search agent to find restaurants.
    
    Uses the search agent with tools to find restaurants
    matching user preferences.
    """
    search_agent = state["search_agent"]
    messages = state["messages"]
    entities = state.get("entities", {})
    last_message = messages[-1].content if messages else ""
    
    result = await search_agent.ainvoke(last_message, {
        **state,
        "entities": entities
    })
    
    return {
        **state,
        "tool_outputs": result.get("tool_outputs", []),
        "current_agent": "search_agent"
    }


async def generate_response(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate the final response to the user.
    
    If the agent has results, use those. Otherwise, generate
    a friendly response using the LLM.
    """
    messages = state["messages"]
    tool_outputs = state.get("tool_outputs", [])
    intent = state.get("intent", "chat")
    
    # If we already have a response from the agent, use it
    if tool_outputs:
        return {
            **state,
            "final_response": "I've found some restaurants for you! Check out the results above."
        }
    
    # Generate a response based on intent
    llm = state["llm"]
    
    if intent == "chat":
        # Simple chat response
        prompt = f"""You are a friendly restaurant assistant. 
        
User message: {messages[-1].content if messages else ''}

Respond in a friendly, helpful way. If they're looking for restaurants, 
encourage them to search for what they're craving!"""
    else:
        # Default response
        prompt = f"""You are a helpful restaurant assistant.

The user wants to: {intent}

Provide a helpful response."""
    
    response = await llm.ainvoke(prompt)
    
    return {
        **state,
        "final_response": response.content
    }


async def handle_error(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle errors in the workflow.
    
    Increments retry count and provides error message.
    """
    retry_count = state.get("retry_count", 0)
    
    return {
        **state,
        "error": "An error occurred while processing your request.",
        "retry_count": retry_count + 1,
        "final_response": "Sorry, I encountered an error. Please try again."
    }
