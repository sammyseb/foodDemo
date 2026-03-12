# Restaurant Agent - LangGraph Orchestration Architecture

## Table of Contents

1. [Overview](#overview)
2. [Architecture Pattern](#architecture-pattern)
3. [Project Structure](#project-structure)
4. [Agent Design](#agent-design)
5. [Graph Orchestration](#graph-orchestration)
6. [Tool Integration](#tool-integration)
7. [Configuration](#configuration)
8. [State Management](#state-management)
9. [Streaming](#streaming)
10. [Deployment](#deployment)

---

## 1. Overview

The LangGraph Agent is the orchestration layer that coordinates the AI-powered restaurant assistant. It uses LangGraph for workflow orchestration and connects to MCP (Model Context Protocol) servers for tool execution.

### 1.1 Responsibilities

| Responsibility | Description |
|---------------|-------------|
| **Intent Classification** | Understand user goals from natural language |
| **Entity Extraction** | Parse location, cuisine, date, etc. from messages |
| **Tool Selection** | Choose appropriate tools based on intent |
| **Response Generation** | Create natural language responses |
| **Session Management** | Maintain conversation context |
| **Streaming** | Real-time response streaming via SSE |

### 1.2 Tech Stack

| Component | Technology | Version |
|-----------|------------|---------|
| Orchestration | LangGraph | 0.2.x |
| Agent Logic | LangChain | 0.3.x |
| LLM | OpenAI | GPT-4o |
| Protocol | MCP | 1.0 |
| Runtime | Python | 3.11+ |
| Async | asyncio | built-in |
| Validation | Pydantic | 2.x |
| Config | PyYAML | 6.x |

---

## 2. Architecture Pattern

### 2.1 Multi-Agent Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      MAIN ORCHESTRATOR                           │
│  ┌───────────────────────────────────────────────────────────┐   │
│  │  Intent Classification → Entity Extraction → Routing     │   │
│  └───────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│   Search      │   │   Details     │   │  Reservation  │
│   Agent       │   │   Agent       │   │   Agent       │
└───────┬───────┘   └───────┬───────┘   └───────┬───────┘
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
                             ▼
                    ┌───────────────┐
                    │    MCP        │
                    │   Tools       │
                    └───────────────┘
```

### 2.2 Agent Flow

```
User Message
      │
      ▼
┌─────────────────┐
│  Intent Router  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Entity Extract  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Tool Agent    │
│  (with tools)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Response     │
│   Generator     │
└────────┬────────┘
         │
         ▼
   Streaming
    Response
```

---

## 3. Project Structure

```
agents/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration
│   └── constants.py            # Constants
├── agents/
│   ├── __init__.py
│   ├── factory.py              # Agent factory
│   ├── router.py               # Intent router agent
│   ├── search.py               # Search agent
│   ├── details.py              # Details agent
│   └── reservation.py          # Reservation agent
├── graph/
│   ├── __init__.py
│   ├── state.py                # State definitions
│   ├── nodes.py                # Graph nodes
│   ├── edges.py                # Graph edges
│   └── builder.py              # Graph builder
├── tools/
│   ├── __init__.py
│   ├── factory.py              # Tool factory
│   ├── search_tools.py         # Search tools
│   ├── mcp_wrapper.py          # MCP tool wrapper
│   └── base.py                 # Base tool classes
├── services/
│   ├── __init__.py
│   ├── llm_service.py          # LLM service
│   ├── session_service.py      # Session management
│   └── streaming_service.py    # SSE streaming
├── models/
│   ├── __init__.py
│   ├── state.py                # State models
│   ├── tools.py                # Tool models
│   └── responses.py            # Response models
├── config/
│   ├── agents.yaml             # Agent configuration
│   ├── prompts.yaml            # Prompt templates
│   └── tools.yaml              # Tool configuration
├── routers/
│   ├── __init__.py
│   └── agent_router.py         # API routes
├── tests/
│   ├── __init__.py
│   ├── agents/
│   ├── graph/
│   └── tools/
├── .env.example
├── pyproject.toml
├── uv.lock
├── Dockerfile
└── README.md
```

---

## 4. Agent Design

### 4.1 Base Agent Structure

```python
# agents/base.py
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain.agents import AgentExecutor


class BaseAgent(ABC):
    """Base class for all agents."""
    
    def __init__(
        self,
        llm,
        tools: list,
        system_prompt: str,
        max_iterations: int = 10
    ):
        self.llm = llm
        self.tools = tools
        self.system_prompt = system_prompt
        self.max_iterations = max_iterations
        self._executor: Optional[AgentExecutor] = None
    
    @abstractmethod
    async def ainvoke(self, input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process input and return result."""
        pass
    
    @abstractmethod
    async def astream(self, input: str, context: Dict[str, Any]):
        """Process input and yield streaming results."""
        pass
    
    @property
    def executor(self) -> AgentExecutor:
        """Get or create agent executor."""
        if self._executor is None:
            self._executor = self._create_executor()
        return self._executor
    
    @abstractmethod
    def _create_executor(self) -> AgentExecutor:
        """Create the agent executor."""
        pass
```

### 4.2 Router Agent

```python
# agents/router.py
from typing import Any, Dict, List
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_openai import ChatOpenAI
from .base import BaseAgent


class RouterAgent(BaseAgent):
    """Routes user requests to appropriate handlers."""
    
    SYSTEM_PROMPT = """You are a restaurant assistant router. 
Analyze the user's message and determine their intent:

INTENTS:
- search: Looking for restaurants (find, search, recommend)
- details: Want specific restaurant information
- reserve: Want to make a reservation
- recommend: Want personalized recommendations
- compare: Want to compare restaurants
- chat: General conversation

Extract any entities:
- location: City, neighborhood, address
- cuisine: Type of food (italian, japanese, etc.)
- price_range: $, $$, $$$, $$$$
- rating: Minimum rating (1-5)
- date: Reservation date
- time: Reservation time
- party_size: Number of guests

Respond in JSON format:
{{"intent": "search", "entities": {{"location": "San Francisco", "cuisine": "italian"}}}}"""
    
    def __init__(self, llm: ChatOpenAI):
        super().__init__(
            llm=llm,
            tools=[],  # Router uses LLM reasoning only
            system_prompt=self.SYSTEM_PROMPT
        )
    
    async def ainvoke(self, input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Classify intent and extract entities."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", "{input}")
        ])
        
        agent = create_tool_calling_agent(self.llm, [], prompt)
        executor = AgentExecutor(
            agent=agent,
            tools=[],
            verbose=False
        )
        
        result = await executor.ainvoke({"input": input})
        
        # Parse intent from response
        return self._parse_response(result.get("output", ""))
    
    async def astream(self, input: str, context: Dict[str, Any]):
        """Stream router response."""
        result = await self.ainvoke(input, context)
        yield {"type": "intent", "data": result}
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse intent and entities from response."""
        # Simplified - use JSON extraction in production
        import json
        import re
        
        # Try to find JSON in response
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        
        # Default to chat intent
        return {"intent": "chat", "entities": {}}
    
    def _create_executor(self) -> AgentExecutor:
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", "{input}")
        ])
        
        agent = create_tool_calling_agent(self.llm, [], prompt)
        return AgentExecutor(agent=agent, tools=[], verbose=False)
```

### 4.3 Search Agent

```python
# agents/search.py
from typing import Any, Dict, List
from langchain.prompts import ChatPromptTemplate
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_openai import ChatOpenAI
from .base import BaseAgent


class SearchAgent(BaseAgent):
    """Handles restaurant search with tools."""
    
    SYSTEM_PROMPT = """You are a restaurant search specialist.
Use the available tools to find restaurants matching user preferences.
Present results in a clear, helpful format.

Available tools:
- search_restaurants: Search by query, location, cuisine
- get_restaurant_details: Get detailed info about a restaurant

Always:
1. Use search_restaurants first to find options
2. Present results with name, rating, price, location
3. Ask follow-up questions if preferences are unclear"""

    def __init__(self, llm: ChatOpenAI, tools: List):
        super().__init__(
            llm=llm,
            tools=tools,
            system_prompt=self.SYSTEM_PROMPT
        )
    
    async def ainvoke(self, input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Search for restaurants."""
        result = await self.executor.ainvoke({"input": input})
        
        return {
            "response": result.get("output", ""),
            "tool_outputs": result.get("tool_outputs", [])
        }
    
    async def astream(self, input: str, context: Dict[str, Any]):
        """Stream search results."""
        # Stream tool outputs
        async for chunk in self._stream_tools(input, context):
            yield chunk
        
        # Stream final response
        result = await self.ainvoke(input, context)
        yield {"type": "content", "text": result["response"]}
    
    async def _stream_tools(self, input: str, context: Dict[str, Any]):
        """Stream tool execution."""
        # Implementation for streaming tool execution
        pass
    
    def _create_executor(self) -> AgentExecutor:
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", "{input}")
        ])
        
        agent = create_tool_calling_agent(self.llm, self.tools, prompt)
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            max_iterations=self.max_iterations
        )
```

---

## 5. Graph Orchestration

### 5.1 State Definition

```python
# graph/state.py
from typing import TypedDict, Annotated, Optional, List, Any
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """State managed by LangGraph."""
    
    # Messages (with automatic message addition)
    messages: Annotated[List[Any], add_messages]
    
    # Session info
    session_id: str
    user_id: str
    
    # Intent & entities
    intent: Optional[str]
    entities: Optional[dict]
    
    # Current agent
    current_agent: str
    
    # Tool execution
    tool_outputs: List[dict]
    
    # Response
    final_response: str
    
    # Error handling
    error: Optional[str]
    retry_count: int
```

### 5.2 Graph Nodes

```python
# graph/nodes.py
from typing import Dict, Any
from langchain_core.messages import HumanMessage, AIMessage


async def classify_intent(state: Dict[str, Any]) -> Dict[str, Any]:
    """Classify user intent using router agent."""
    messages = state["messages"]
    last_message = messages[-1].content if messages else ""
    
    router_agent = state["router_agent"]
    result = await router_agent.ainvoke(last_message, state)
    
    return {
        **state,
        "intent": result.get("intent", "chat"),
        "entities": result.get("entities", {})
    }


async def route_by_intent(state: Dict[str, Any]) -> str:
    """Route to appropriate agent based on intent."""
    intent = state.get("intent", "chat")
    
    mapping = {
        "search": "search_agent",
        "recommend": "search_agent",
        "compare": "search_agent",
        "details": "details_agent",
        "reserve": "reservation_agent",
        "chat": "generate_response"
    }
    
    return mapping.get(intent, "generate_response")


async def execute_search(state: Dict[str, Any]) -> Dict[str, Any]:
    """Execute search agent."""
    search_agent = state["search_agent"]
    messages = state["messages"]
    last_message = messages[-1].content if messages else ""
    
    result = await search_agent.ainvoke(last_message, state)
    
    return {
        **state,
        "tool_outputs": result.get("tool_outputs", []),
        "current_agent": "search_agent"
    }


async def execute_details(state: Dict[str, Any]) -> Dict[str, Any]:
    """Execute details agent."""
    details_agent = state["details_agent"]
    messages = state["messages"]
    last_message = messages[-1].content if messages else ""
    
    result = await details_agent.ainvoke(last_message, state)
    
    return {
        **state,
        "tool_outputs": result.get("tool_outputs", []),
        "current_agent": "details_agent"
    }


async def execute_reservation(state: Dict[str, Any]) -> Dict[str, Any]:
    """Execute reservation agent."""
    reservation_agent = state["reservation_agent"]
    messages = state["messages"]
    last_message = messages[-1].content if messages else ""
    
    result = await reservation_agent.ainvoke(last_message, state)
    
    return {
        **state,
        "tool_outputs": result.get("tool_outputs", []),
        "current_agent": "reservation_agent"
    }


async def generate_response(state: Dict[str, Any]) -> Dict[str, Any]:
    """Generate final response."""
    messages = state["messages"]
    tool_outputs = state.get("tool_outputs", [])
    
    # Use LLM to generate friendly response
    llm = state["llm"]
    
    prompt = f"""Generate a friendly response to the user's message.
    
Recent messages:
{chr(10).join([f"{m.type}: {m.content}" for m in messages[-3:]])}

Tool outputs: {tool_outputs}

Provide a natural, helpful response."""
    
    response = await llm.ainvoke(prompt)
    
    return {
        **state,
        "final_response": response.content
    }
```

### 5.3 Graph Builder

```python
# graph/builder.py
from langgraph.graph import StateGraph, END
from .state import AgentState
from .nodes import (
    classify_intent,
    route_by_intent,
    execute_search,
    execute_details,
    execute_reservation,
    generate_response
)


def create_agent_graph(
    router_agent,
    search_agent,
    details_agent,
    reservation_agent,
    llm
) -> StateGraph:
    """Build the LangGraph workflow."""
    
    graph = StateGraph(AgentState)
    
    # Add nodes
    graph.add_node("classify_intent", classify_intent)
    graph.add_node("search_agent", execute_search)
    graph.add_node("details_agent", execute_details)
    graph.add_node("reservation_agent", execute_reservation)
    graph.add_node("generate_response", generate_response)
    
    # Set entry point
    graph.set_entry_point("classify_intent")
    
    # Route to appropriate agent
    graph.add_edge("classify_intent", "route_by_intent")
    
    # Conditional routing
    graph.add_conditional_edges(
        "route_by_intent",
        route_by_intent,
        {
            "search_agent": "search_agent",
            "details_agent": "details_agent",
            "reservation_agent": "reservation_agent",
            "generate_response": "generate_response"
        }
    )
    
    # All agents lead to response generation
    graph.add_edge("search_agent", "generate_response")
    graph.add_edge("details_agent", "generate_response")
    graph.add_edge("reservation_agent", "generate_response")
    
    # End
    graph.add_edge("generate_response", END)
    
    # Compile
    return graph.compile()


def create_initial_state(
    message: str,
    session_id: str,
    user_id: str,
    router_agent,
    search_agent,
    details_agent,
    reservation_agent,
    llm
) -> AgentState:
    """Create initial state for the graph."""
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
        "details_agent": details_agent,
        "reservation_agent": reservation_agent,
        "llm": llm
    }
```

---

## 6. Tool Integration

### 6.1 MCP Tool Wrapper

```python
# tools/mcp_wrapper.py
from typing import Any, Dict, Optional, AsyncIterator
import aiohttp
import json


class MCPToolWrapper:
    """Wrapper for MCP tools to use with LangChain."""
    
    def __init__(
        self,
        name: str,
        description: str,
        mcp_server_url: str,
        mcp_tool_name: str,
        api_key: Optional[str] = None
    ):
        self.name = name
        self.description = description
        self.mcp_server_url = mcp_server_url
        self.mcp_tool_name = mcp_tool_name
        self.api_key = api_key
    
    async def ainvoke(self, input_str: str) -> str:
        """Execute the tool."""
        # Parse input
        try:
            params = json.loads(input_str) if input_str else {}
        except json.JSONDecodeError:
            params = {"query": input_str}
        
        # Call MCP server
        results = []
        async for chunk in self._call_mcp(params):
            results.append(chunk)
        
        return self._format_results(results)
    
    async def _call_mcp(self, params: dict) -> AsyncIterator[dict]:
        """Call MCP server."""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.mcp_server_url}/mcp",
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {
                        "name": self.mcp_tool_name,
                        "arguments": params
                    }
                },
                headers=headers
            ) as response:
                async for line in response.content:
                    if line:
                        try:
                            data = json.loads(line)
                            if "result" in data:
                                yield data["result"]
                        except json.JSONDecodeError:
                            continue
    
    def _format_results(self, results: list) -> str:
        """Format tool results for the agent."""
        if not results:
            return "No results found."
        
        formatted = []
        for r in results:
            if isinstance(r, dict):
                formatted.append(
                    f"- {r.get('name', 'Restaurant')}: "
                    f"⭐ {r.get('rating', 'N/A')} | "
                    f"{r.get('vicinity', r.get('address', ''))}"
                )
        
        return "\n".join(formatted) if formatted else str(results)
    
    @property
    def args_schema(self) -> type:
        """Get argument schema for this tool."""
        from pydantic import BaseModel
        
        class ToolInput(BaseModel):
            query: Optional[str] = None
            location: Optional[str] = None
        
        return ToolInput
```

### 6.2 Tool Factory

```python
# tools/factory.py
from typing import List
from langchain.tools import Tool
from .mcp_wrapper import MCPToolWrapper
from app.config import settings


class ToolFactory:
    """Factory for creating tools from configuration."""
    
    def __init__(self, mcp_server_url: str, mcp_api_key: str):
        self.mcp_server_url = mcp_server_url
        self.mcp_api_key = mcp_api_key
    
    def create_search_tools(self) -> List[Tool]:
        """Create restaurant search tools."""
        
        # Search restaurants tool
        search_tool = MCPToolWrapper(
            name="search_restaurants",
            description="Search for restaurants by query, location, cuisine, price range, or rating",
            mcp_server_url=self.mcp_server_url,
            mcp_tool_name="search_restaurants",
            api_key=self.mcp_api_key
        )
        
        # Get restaurant details tool
        details_tool = MCPToolWrapper(
            name="get_restaurant_details",
            description="Get detailed information about a specific restaurant",
            mcp_server_url=self.mcp_server_url,
            mcp_tool_name="get_place_details",
            api_key=self.mcp_api_key
        )
        
        return [
            Tool(
                name="search_restaurants",
                description=search_tool.description,
                args_schema=search_tool.args_schema,
                coroutine=search_tool.ainvoke
            ),
            Tool(
                name="get_restaurant_details",
                description=details_tool.description,
                args_schema=details_tool.args_schema,
                coroutine=details_tool.ainvoke
            )
        ]
    
    def create_reservation_tools(self) -> List[Tool]:
        """Create reservation tools."""
        # Implementation for reservation tools
        return []
```

---

## 7. Configuration

### 7.1 YAML Configuration

Create `config/agents.yaml`:

```yaml
version: "1.0"

# LLM Configuration
llm:
  provider: "openai"
  model: "gpt-4o"
  temperature: 0.7
  max_tokens: 2000

# Agent Configurations
agents:
  router:
    description: "Routes user requests to appropriate handlers"
    system_prompt: |
      You are a restaurant assistant router. Analyze the user's 
      message and determine their intent...
    tools: []
    max_iterations: 3

  search:
    description: "Searches for restaurants"
    system_prompt: |
      You are a restaurant search specialist. Use the available 
      tools to find restaurants...
    tools:
      - search_restaurants
      - get_restaurant_details
    max_iterations: 10

  details:
    description: "Gets restaurant details"
    system_prompt: |
      You provide detailed restaurant information...
    tools:
      - get_restaurant_details
    max_iterations: 5

  reservation:
    description: "Makes reservations"
    system_prompt: |
      Help users make reservations...
    tools: []
    max_iterations: 10

# Tool Configurations  
tools:
  search_restaurants:
    mcp_server: "google_places"
    mcp_tool: "search_restaurants"
    description: "Search for restaurants"
    default_radius: 5000
    max_results: 10

  get_restaurant_details:
    mcp_server: "google_places"
    mcp_tool: "get_place_details"
    description: "Get restaurant details"
```

### 7.2 Configuration Loader

```python
# app/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache
import yaml
from pathlib import Path


class Settings(BaseSettings):
    # App
    app_name: str = "Restaurant Agent"
    version: str = "1.0.0"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8001
    
    # LLM
    openai_api_key: str
    
    # MCP
    mcp_server_url: str = "http://localhost:8002"
    mcp_api_key: str = ""
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"


def load_agent_config(path: str = "config/agents.yaml") -> dict:
    """Load agent configuration from YAML."""
    with open(path) as f:
        return yaml.safe_load(f)


@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

---

## 8. State Management

### 8.1 Session Service

```python
# services/session_service.py
from typing import Dict, Any, Optional
from datetime import datetime
import uuid


class SessionService:
    """Manages conversation sessions."""
    
    def __init__(self):
        self._sessions: Dict[str, Dict[str, Any]] = {}
    
    def create_session(self, user_id: str) -> str:
        """Create a new session."""
        session_id = str(uuid.uuid4())
        self._sessions[session_id] = {
            "id": session_id,
            "user_id": user_id,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "message_count": 0,
            "context": {}
        }
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session by ID."""
        return self._sessions.get(session_id)
    
    def update_session(self, session_id: str, updates: Dict[str, Any]):
        """Update session."""
        if session_id in self._sessions:
            self._sessions[session_id].update(updates)
            self._sessions[session_id]["updated_at"] = datetime.utcnow()
    
    def delete_session(self, session_id: str):
        """Delete session."""
        self._sessions.pop(session_id, None)
    
    def get_user_sessions(self, user_id: str) -> list:
        """Get all sessions for a user."""
        return [
            s for s in self._sessions.values()
            if s["user_id"] == user_id
        ]
```

---

## 9. Streaming

### 9.1 Streaming Service

```python
# services/streaming_service.py
from typing import AsyncGenerator
import json


class StreamingService:
    """Handles SSE streaming responses."""
    
    async def stream_response(
        self,
        generator: AsyncGenerator[dict, None]
    ) -> AsyncGenerator[str, None]:
        """Convert async generator to SSE format."""
        async for chunk in generator:
            yield f"data: {json.dumps(chunk)}\n\n"
        
        yield "data: [DONE]\n\n"
    
    async def stream_agent(
        self,
        agent,
        input: str,
        context: dict
    ) -> AsyncGenerator[dict, None]:
        """Stream agent execution."""
        # Stream intent classification
        intent_result = await agent.router_agent.ainvoke(input, context)
        yield {"type": "intent", "data": intent_result}
        
        # Stream agent execution
        agent_name = self._route_intent(intent_result)
        
        if agent_name == "search_agent":
            async for chunk in agent.search_agent.astream(input, context):
                yield chunk
        elif agent_name == "details_agent":
            async for chunk in agent.details_agent.astream(input, context):
                yield chunk
        elif agent_name == "reservation_agent":
            async for chunk in agent.reservation_agent.astream(input, context):
                yield chunk
        else:
            # Generate response directly
            response = await agent.llm.ainvoke(input)
            yield {"type": "content", "text": response.content}
```

---

## 10. Deployment

### 10.1 FastAPI App

```python
# app/main.py
from fastapi import FastAPI, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import json

from app.config import get_settings, load_agent_config
from agents.factory import AgentFactory
from graph.builder import create_agent_graph
from services.session_service import SessionService


app = FastAPI(title="Restaurant Agent")


# Initialize on startup
@app.on_event("startup")
async def startup():
    settings = get_settings()
    agent_config = load_agent_config()
    
    # Create agents
    factory = AgentFactory(settings, agent_config)
    app.state.agent = factory.create_agent()
    app.state.session_service = SessionService()


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


@app.post("/agent/chat")
async def chat(request: ChatRequest):
    """Non-streaming chat endpoint."""
    agent = app.state.agent
    session_service = app.state.session_service
    
    # Get or create session
    session_id = request.session_id or session_service.create_session_id("user")
    
    result = await agent.ainvoke(
        message=request.message,
        session_id=session_id,
        user_id="user"
    )
    
    return {
        "message": result.get("output", ""),
        "session_id": session_id
    }


@app.post("/agent/chat/stream")
async def chat_stream(request: ChatRequest):
    """Streaming chat endpoint."""
    agent = app.state.agent
    session_service = app.state.session_service
    
    session_id = request.session_id or session_service.create_session_id("user")
    
    async def event_generator():
        yield f"data: {json.dumps({'type': 'session_id', 'session_id': session_id})}\n\n"
        
        try:
            async for chunk in agent.astream(request.message, session_id, "user"):
                yield f"data: {json.dumps(chunk)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
        
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
```

### 10.2 Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY . .

EXPOSE 8001

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
```

---

## Summary

The LangGraph Agent provides:

| Feature | Implementation |
|---------|---------------|
| **Intent Classification** | Router agent with LLM |
| **Entity Extraction** | Parser in router |
| **Tool Integration** | MCP wrapper for LangChain |
| **Graph Orchestration** | LangGraph StateGraph |
| **Session Management** | SessionService |
| **Streaming** | SSE via FastAPI |
| **Configuration** | YAML-based agents config |
| **Error Handling** | Retry logic in nodes |

---

## Next Steps

- See [Implementation Plan](./Implementation-Plan.md) for step-by-step guide
- Configure MCP server connection
- Add more agent types
- Implement advanced features
