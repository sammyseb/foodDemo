# Restaurant Agent - LangGraph Implementation Plan

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Phase 1: Project Setup](#phase-1-project-setup)
4. [Phase 2: Core Infrastructure](#phase-2-core-infrastructure)
5. [Phase 3: Agent Design](#phase-3-agent-design)
6. [Phase 4: Graph Orchestration](#phase-4-graph-orchestration)
7. [Phase 5: Tool Integration](#phase-5-tool-integration)
8. [Phase 6: Configuration](#phase-6-configuration)
9. [Phase 7: API & Streaming](#phase-7-api--streaming)
10. [Phase 8: Testing](#phase-8-testing)
11. [Phase 9: Deployment](#phase-9-deployment)
12. [Checklist](#checklist)

---

## 1. Overview

This plan provides step-by-step instructions to build the LangGraph orchestration layer for the Restaurant Agent.

**Estimated Total Time**: 2-3 weeks
**Difficulty**: Advanced

---

## 2. Prerequisites

### 2.1 Required Tools

```bash
# Python 3.11+
python --version

# uv package manager
pip install uv
```

### 2.2 Dependencies

```toml
# Core LangGraph/LangChain
langgraph>=0.2.0
langchain>=0.3.0
langchain-openai>=0.2.0

# MCP
aiohttp>=3.9.0

# FastAPI
fastapi>=0.109.0
uvicorn[standard]>=0.27.0

# Config
pyyaml>=6.0

# Validation
pydantic>=2.0.0

# Testing
pytest>=8.0.0
pytest-asyncio>=0.23.0
```

---

## 3. Phase 1: Project Setup

**Duration**: 1-2 hours
**Goals**: Initialize project, dependencies

### 3.1 Create Project

```bash
mkdir -p agents
cd agents

cat > pyproject.toml << 'EOF'
[project]
name = "restaurant-agent"
version = "1.0.0"
description = "Restaurant Agent with LangGraph"
requires-python = ">=3.11"
dependencies = [
    "langgraph>=0.2.0",
    "langchain>=0.3.0",
    "langchain-openai>=0.2.0",
    "langchain-core>=0.3.0",
    "aiohttp>=3.9.0",
    "fastapi>=0.109.0",
    "uvicorn[standard]>=0.27.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "pyyaml>=6.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "pytest-cov>=4.1.0",
    "ruff>=0.1.0",
]

[tool.uv]
dev-dependencies = []

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
EOF

# Install dependencies
uv sync
```

### 3.2 Create Environment

```bash
cat > .env.example << 'EOF'
# LLM
OPENAI_API_KEY=sk-...

# MCP Server
MCP_SERVER_URL=http://localhost:8002
MCP_API_KEY=

# Server
HOST=0.0.0.0
PORT=8001

# Logging
LOG_LEVEL=INFO
EOF

cp .env.example .env
```

### 3.3 Create Directory Structure

```bash
mkdir -p app
mkdir -p agents
mkdir -p graph
mkdir -p tools
mkdir -p services
mkdir -p models
mkdir -p config
mkdir -p routers
mkdir -p tests/{agents,graph,tools}
```

### 3.4 Create Init Files

```bash
touch app/__init__.py
touch agents/__init__.py
touch graph/__init__.py
touch tools/__init__.py
touch services/__init__.py
touch models/__init__.py
touch routers/__init__.py
touch tests/__init__.py
```

---

## 4. Phase 2: Core Infrastructure

**Duration**: 2-3 hours
**Goals**: Config, base classes

### 4.1 Configuration

Create `app/config.py`:

```python
from pydantic_settings import BaseSettings
from functools import lru_cache
import yaml
from pathlib import Path


class Settings(BaseSettings):
    openai_api_key: str
    mcp_server_url: str = "http://localhost:8002"
    mcp_api_key: str = ""
    host: str = "0.0.0.0"
    port: int = 8001
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"


def load_agent_config(path: str = "config/agents.yaml") -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

### 4.2 Domain Models

Create `models/state.py`:

```python
from typing import TypedDict, Annotated, Optional, List, Any
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """State managed by LangGraph."""
    
    messages: Annotated[List[Any], add_messages]
    session_id: str
    user_id: str
    intent: Optional[str]
    entities: Optional[dict]
    current_agent: str
    tool_outputs: List[dict]
    final_response: str
    error: Optional[str]
    retry_count: int
```

Create `models/tools.py`:

```python
from pydantic import BaseModel, Field
from typing import Optional


class SearchInput(BaseModel):
    query: Optional[str] = None
    location: Optional[str] = None
    cuisine: Optional[str] = None
    radius: int = Field(5000, ge=100, le=50000)
    limit: int = Field(10, ge=1, le=50)


class RestaurantDetailInput(BaseModel):
    place_id: str
```

---

## 5. Phase 3: Agent Design

**Duration**: 3-4 hours
**Goals**: Router, Search, Details agents

### 5.1 Base Agent

Create `agents/base.py`:

```python
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
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
        pass
    
    @abstractmethod
    async def astream(self, input: str, context: Dict[str, Any]):
        pass
```

### 5.2 Router Agent

Create `agents/router.py`:

```python
from typing import Any, Dict
from langchain.prompts import ChatPromptTemplate
from langchain.agents import AgentExecutor, create_tool_calling_agent
from .base import BaseAgent


class RouterAgent(BaseAgent):
    """Routes user requests to appropriate handlers."""
    
    SYSTEM_PROMPT = """You are a restaurant assistant router.
Analyze the user's message and determine their intent.

INTENTS:
- search: Looking for restaurants
- details: Want restaurant information
- reserve: Make a reservation
- recommend: Personalized recommendations
- chat: General conversation

Extract entities (location, cuisine, date, time, party_size).

Respond in JSON format:
{"intent": "search", "entities": {"location": "SF", "cuisine": "italian"}}"""
    
    def __init__(self, llm):
        super().__init__(llm=llm, tools=[], system_prompt=self.SYSTEM_PROMPT)
    
    async def ainvoke(self, input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", "{input}")
        ])
        
        agent = create_tool_calling_agent(self.llm, [], prompt)
        executor = AgentExecutor(agent=agent, tools=[], verbose=False)
        
        result = await executor.ainvoke({"input": input})
        
        return self._parse_response(result.get("output", ""))
    
    async def astream(self, input: str, context: Dict[str, Any]):
        result = await self.ainvoke(input, context)
        yield {"type": "intent", "data": result}
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        import json
        import re
        
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        
        return {"intent": "chat", "entities": {}}
    
    def _create_executor(self) -> AgentExecutor:
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", "{input}")
        ])
        
        agent = create_tool_calling_agent(self.llm, [], prompt)
        return AgentExecutor(agent=agent, tools=[])
```

### 5.3 Search Agent

Create `agents/search.py`:

```python
from typing import Any, Dict, List
from langchain.prompts import ChatPromptTemplate
from langchain.agents import AgentExecutor, create_tool_calling_agent
from .base import BaseAgent


class SearchAgent(BaseAgent):
    """Handles restaurant search."""
    
    SYSTEM_PROMPT = """You are a restaurant search specialist.
Use the search_restaurants tool to find restaurants.

Present results with name, rating, price, location."""

    def __init__(self, llm, tools: List):
        super().__init__(
            llm=llm,
            tools=tools,
            system_prompt=self.SYSTEM_PROMPT
        )
    
    async def ainvoke(self, input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        result = await self.executor.ainvoke({"input": input})
        
        return {
            "response": result.get("output", ""),
            "tool_outputs": result.get("tool_outputs", [])
        }
    
    async def astream(self, input: str, context: Dict[str, Any]):
        result = await self.ainvoke(input, context)
        yield {"type": "content", "text": result["response"]}
    
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

### 5.4 Agent Factory

Create `agents/factory.py`:

```python
from langchain_openai import ChatOpenAI
from .router import RouterAgent
from .search import SearchAgent
from tools.factory import ToolFactory
from app.config import Settings, load_agent_config


class AgentFactory:
    """Factory for creating configured agents."""
    
    def __init__(self, settings: Settings, config: dict):
        self.settings = settings
        self.config = config
        self._llm = None
        self._tools = None
    
    @property
    def llm(self) -> ChatOpenAI:
        if self._llm is None:
            llm_config = self.config.get("llm", {})
            self._llm = ChatOpenAI(
                model=llm_config.get("model", "gpt-4o"),
                temperature=llm_config.get("temperature", 0.7),
                max_tokens=llm_config.get("max_tokens", 2000)
            )
        return self._llm
    
    @property
    def tools(self):
        if self._tools is None:
            factory = ToolFactory(
                self.settings.mcp_server_url,
                self.settings.mcp_api_key
            )
            self._tools = factory.create_search_tools()
        return self._tools
    
    def create_router(self) -> RouterAgent:
        return RouterAgent(self.llm)
    
    def create_search(self) -> SearchAgent:
        return SearchAgent(self.llm, self.tools)
    
    def create_all(self):
        return {
            "router": self.create_router(),
            "search": self.create_search(),
        }
```

---

## 6. Phase 4: Graph Orchestration

**Duration**: 2-3 hours
**Goals**: State, nodes, edges

### 6.1 Graph Nodes

Create `graph/nodes.py`:

```python
from typing import Dict, Any


async def classify_intent(state: Dict[str, Any]) -> Dict[str, Any]:
    """Classify user intent."""
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
    """Route to appropriate agent."""
    intent = state.get("intent", "chat")
    
    mapping = {
        "search": "search_agent",
        "recommend": "search_agent",
        "details": "search_agent",
        "reserve": "search_agent",
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


async def generate_response(state: Dict[str, Any]) -> Dict[str, Any]:
    """Generate final response."""
    messages = state["messages"]
    tool_outputs = state.get("tool_outputs", [])
    llm = state["llm"]
    
    prompt = f"""Generate a friendly response.
    
Messages: {messages}
Tool outputs: {tool_outputs}

Provide a helpful response."""
    
    response = await llm.ainvoke(prompt)
    
    return {
        **state,
        "final_response": response.content
    }
```

### 6.2 Graph Builder

Create `graph/builder.py`:

```python
from langgraph.graph import StateGraph, END
from .state import AgentState
from .nodes import (
    classify_intent,
    route_by_intent,
    execute_search,
    generate_response
)


def create_agent_graph(router_agent, search_agent, llm) -> StateGraph:
    """Build the LangGraph workflow."""
    
    graph = StateGraph(AgentState)
    
    # Add nodes
    graph.add_node("classify_intent", classify_intent)
    graph.add_node("search_agent", execute_search)
    graph.add_node("generate_response", generate_response)
    
    # Set entry point
    graph.set_entry_point("classify_intent")
    
    # Route
    graph.add_edge("classify_intent", "route_by_intent")
    
    # Conditional routing
    graph.add_conditional_edges(
        "route_by_intent",
        route_by_intent,
        {
            "search_agent": "search_agent",
            "generate_response": "generate_response"
        }
    )
    
    # Edges
    graph.add_edge("search_agent", "generate_response")
    graph.add_edge("generate_response", END)
    
    return graph.compile()


def create_initial_state(message: str, session_id: str, user_id: str, agents: dict, llm) -> AgentState:
    """Create initial state."""
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
        "router_agent": agents["router"],
        "search_agent": agents["search"],
        "llm": llm
    }
```

---

## 7. Phase 5: Tool Integration

**Duration**: 2-3 hours
**Goals**: MCP wrapper, tool factory

### 7.1 MCP Tool Wrapper

Create `tools/mcp_wrapper.py`:

```python
from typing import Any, Dict, Optional, AsyncIterator
import aiohttp
import json


class MCPToolWrapper:
    """Wrapper for MCP tools."""
    
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
        try:
            params = json.loads(input_str) if input_str else {}
        except json.JSONDecodeError:
            params = {"query": input_str}
        
        results = []
        async for chunk in self._call_mcp(params):
            results.append(chunk)
        
        return self._format_results(results)
    
    async def _call_mcp(self, params: dict) -> AsyncIterator[dict]:
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
        if not results:
            return "No results found."
        
        formatted = []
        for r in results:
            if isinstance(r, dict):
                name = r.get("name", "Restaurant")
                rating = r.get("rating", "N/A")
                address = r.get("vicinity", r.get("address", ""))
                formatted.append(f"- {name}: ⭐ {rating} | {address}")
        
        return "\n".join(formatted) if formatted else str(results)
```

### 7.2 Tool Factory

Create `tools/factory.py`:

```python
from typing import List
from langchain.tools import Tool
from .mcp_wrapper import MCPToolWrapper


class ToolFactory:
    def __init__(self, mcp_server_url: str, mcp_api_key: str):
        self.mcp_server_url = mcp_server_url
        self.mcp_api_key = mcp_api_key
    
    def create_search_tools(self) -> List[Tool]:
        search_tool = MCPToolWrapper(
            name="search_restaurants",
            description="Search for restaurants by query, location, cuisine",
            mcp_server_url=self.mcp_server_url,
            mcp_tool_name="search_restaurants",
            api_key=self.mcp_api_key
        )
        
        details_tool = MCPToolWrapper(
            name="get_restaurant_details",
            description="Get restaurant details",
            mcp_server_url=self.mcp_server_url,
            mcp_tool_name="get_place_details",
            api_key=self.mcp_api_key
        )
        
        return [
            Tool(
                name="search_restaurants",
                description=search_tool.description,
                coroutine=search_tool.ainvoke
            ),
            Tool(
                name="get_restaurant_details",
                description=details_tool.description,
                coroutine=details_tool.ainvoke
            )
        ]
```

---

## 8. Phase 6: Configuration

**Duration**: 1 hour
**Goals**: YAML config files

### 8.1 Agent Configuration

Create `config/agents.yaml`:

```yaml
version: "1.0"

llm:
  provider: "openai"
  model: "gpt-4o"
  temperature: 0.7
  max_tokens: 2000

agents:
  router:
    description: "Routes user requests"
    system_prompt: |
      You are a restaurant assistant router...
    tools: []
    max_iterations: 3

  search:
    description: "Searches for restaurants"
    system_prompt: |
      You are a restaurant search specialist...
    tools:
      - search_restaurants
      - get_restaurant_details
    max_iterations: 10

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

---

## 9. Phase 7: API & Streaming

**Duration**: 2-3 hours
**Goals**: FastAPI app with streaming

### 9.1 Main Application

Create `app/main.py`:

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import json
import uuid

from app.config import get_settings, load_agent_config
from agents.factory import AgentFactory
from graph.builder import create_agent_graph


app = FastAPI(title="Restaurant Agent")

# State
agents = {}


@app.on_event("startup")
async def startup():
    settings = get_settings()
    agent_config = load_agent_config()
    
    factory = AgentFactory(settings, agent_config)
    agents["factory"] = factory
    agents["graph"] = create_agent_graph(
        factory.create_router(),
        factory.create_search(),
        factory.llm
    )


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


@app.post("/agent/chat")
async def chat(request: ChatRequest):
    """Non-streaming chat."""
    session_id = request.session_id or str(uuid.uuid4())
    
    from langchain_core.messages import HumanMessage
    from graph.builder import create_initial_state
    
    factory = agents["factory"]
    initial_state = create_initial_state(
        message=request.message,
        session_id=session_id,
        user_id="user",
        agents=factory.create_all(),
        llm=factory.llm
    )
    
    result = await agents["graph"].ainvoke(initial_state)
    
    return {
        "message": result.get("final_response", ""),
        "session_id": session_id,
        "intent": result.get("intent")
    }


@app.post("/agent/chat/stream")
async def chat_stream(request: ChatRequest):
    """Streaming chat."""
    session_id = request.session_id or str(uuid.uuid4())
    
    async def event_generator():
        yield f"data: {json.dumps({'type': 'session_id', 'session_id': session_id})}\n\n"
        
        try:
            factory = agents["factory"]
            from graph.builder import create_initial_state
            
            initial_state = create_initial_state(
                message=request.message,
                session_id=session_id,
                user_id="user",
                agents=factory.create_all(),
                llm=factory.llm
            )
            
            async for chunk in agents["graph"].astream(initial_state):
                if "final_response" in chunk:
                    yield f"data: {json.dumps({'type': 'content', 'text': chunk['final_response']})}\n\n"
                elif "intent" in chunk:
                    yield f"data: {json.dumps({'type': 'intent', 'data': chunk.get('intent')})}\n\n"
                    
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
        
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )


@app.get("/health")
async def health():
    return {"status": "healthy"}
```

---

## 10. Phase 8: Testing

**Duration**: 2-3 hours
**Goals**: Unit tests

### 10.1 Test Setup

Create `tests/conftest.py`:

```python
import pytest
from unittest.mock import Mock, AsyncMock


@pytest.fixture
def mock_llm():
    llm = Mock()
    llm.ainvoke = AsyncMock(return_value=Mock(content="Test response"))
    return llm


@pytest.fixture
def mock_tools():
    tool = Mock()
    tool.name = "search_restaurants"
    tool.ainvoke = AsyncMock(return_value="Restaurant: Test")
    return [tool]
```

### 10.2 Agent Tests

Create `tests/agents/test_router.py`:

```python
import pytest
from agents.router import RouterAgent


@pytest.mark.asyncio
async def test_router_parses_intent(mock_llm):
    agent = RouterAgent(mock_llm)
    
    result = await agent.ainvoke("Find Italian restaurants in SF", {})
    
    assert "intent" in result
    assert "entities" in result
```

---

## 11. Phase 9: Deployment

**Duration**: 1-2 hours
**Goals**: Docker, run

### 11.1 Dockerfile

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

### 11.2 Run

```bash
# Build
docker build -t restaurant-agent .

# Run
docker run -p 8001:8001 \
  -e OPENAI_API_KEY=sk-... \
  -e MCP_SERVER_URL=http://mcp:8002 \
  restaurant-agent
```

---

## 12. Checklist

### Phase 1: Project Setup
- [ ] Create pyproject.toml
- [ ] Create .env file
- [ ] Install dependencies
- [ ] Create directory structure

### Phase 2: Core Infrastructure
- [ ] Create config.py
- [ ] Create domain models

### Phase 3: Agent Design
- [ ] Create base agent
- [ ] Create router agent
- [ ] Create search agent
- [ ] Create agent factory

### Phase 4: Graph Orchestration
- [ ] Create graph nodes
- [ ] Create graph builder

### Phase 5: Tool Integration
- [ ] Create MCP wrapper
- [ ] Create tool factory

### Phase 6: Configuration
- [ ] Create agents.yaml

### Phase 7: API & Streaming
- [ ] Create FastAPI app
- [ ] Implement streaming endpoint

### Phase 8: Testing
- [ ] Create test fixtures
- [ ] Write unit tests

### Phase 9: Deployment
- [ ] Create Dockerfile
- [ ] Build and test

---

## Next Steps

- Add more agent types (details, reservation)
- Improve intent classification
- Add session persistence
- Configure production deployment
