# Restaurant Agent Framework Design Document

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Architecture Overview](#system-architecture-overview)
3. [Technical Stack](#technical-stack)
4. [MCP Server Integration Design](#mcp-server-integration-design)
5. [LangGraph Agent Architecture](#langgraph-agent-architecture)
6. [ReAct Agent Tool Schema](#react-agent-tool-schema)
7. [Data Models](#data-models)
8. [Workflow Design](#workflow-design)
9. [API Design](#api-design)
10. [Error Handling & Resilience](#error-handling--resilience)
11. [Security Considerations](#security-considerations)
12. [Implementation Roadmap](#implementation-roadmap)
13. [Alternatives & Trade-offs](#alternatives--trade-offs)

---

## 1. Executive Summary

This design document outlines a comprehensive framework for building an AI-powered restaurant assistant using LangGraph and Model Context Protocol (MCP). The system enables users to search restaurants, analyze reviews, receive personalized recommendations, and make reservations through a natural language interface.

**Core Capabilities:**
- **Restaurant Search**: Find restaurants by cuisine, location, price range, rating
- **Review Analysis**: Aggregate and analyze reviews from multiple sources
- **Recommendations**: AI-powered personalized recommendations based on preferences
- **Reservations**: Make table reservations at partner restaurants

**Key Technologies:**
- LangGraph for agent orchestration
- LangChain ReAct agent for reasoning and action
- MCP (Model Context Protocol) via HTTP/SSE for server communication
- OpenAI GPT models for natural language understanding

---

## 2. System Architecture Overview

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                    │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────┐ │
│  │   Web Client    │  │  Mobile App     │  │    CLI / API Consumer       │ │
│  └────────┬────────┘  └────────┬────────┘  └──────────────┬──────────────┘ │
└───────────┼────────────────────┼─────────────────────────┼──────────────────┘
            │                    │                         │
            ▼                    ▼                         ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│                            API GATEWAY                                        │
│  ┌──────────────────────────────────────────────────────────────────────────┐ │
│  │  • Authentication & Authorization                                         │ │
│  │  • Rate Limiting & Quotas                                                │ │
│  │  • Request Validation                                                    │ │
│  │  • SSL/TLS Termination                                                  │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────┬───────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         LANGGRAPH ORCHESTRATION LAYER                        │
│  ┌──────────────────────────────────────────────────────────────────────────┐ │
│  │                           ┌─────────────────┐                            │ │
│  │                           │   Agent State   │                            │ │
│  │                           │   (LangGraph)   │                            │ │
│  │                           └────────┬────────┘                            │ │
│  │                                    │                                      │ │
│  │         ┌──────────────────────────┼──────────────────────────┐         │ │
│  │         │                          │                          │         │ │
│  │         ▼                          ▼                          ▼         │ │
│  │  ┌─────────────┐           ┌─────────────┐           ┌─────────────┐   │ │
│  │  │   Router   │           │   Router    │           │   Router    │   │ │
│  │  │   Node     │           │   Node      │           │   Node      │   │ │
│  │  └──────┬──────┘           └──────┬──────┘           └──────┬──────┘   │ │
│  │         │                         │                         │          │ │
│  │         ▼                         ▼                         ▼          │ │
│  │  ┌─────────────┐           ┌─────────────┐           ┌─────────────┐   │ │
│  │  │  Search    │           │  Analyze    │           │ Reserve    │   │ │
│  │  │  Sub-Agent │           │  Sub-Agent  │           │  Sub-Agent │   │ │
│  │  └──────┬──────┘           └──────┬──────┘           └──────┬──────┘   │ │
│  └─────────┼─────────────────────────┼───────────────────────┼──────────┘ │
└────────────┼──────────────────────────┼──────────────────────┼─────────────┘
             │                          │                      │
             ▼                          ▼                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MCP CLIENT LAYER (HTTP/SSE)                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────┐ │
│  │  Restaurant MCP │  │   Review MCP    │  │      Reservation MCP       │ │
│  │    Server       │  │    Server       │  │         Server             │ │
│  │  (HTTP Stream)  │  │  (HTTP Stream)  │  │     (HTTP Stream)          │ │
│  └────────┬────────┘  └────────┬────────┘  └──────────────┬──────────────┘ │
└───────────┼────────────────────┼─────────────────────────┼──────────────────┘
            │                    │                         │
            ▼                    ▼                         ▼
      ┌─────────────────────────────────────────────────────────────────────┐
      │                      EXTERNAL SERVICES                              │
      │  • Restaurant Database  • Review Aggregators  • Booking Systems   │
      └─────────────────────────────────────────────────────────────────────┘
```

### 2.2 Architecture Layers

| Layer | Responsibility | Key Components |
|-------|---------------|----------------|
| Client | User interface, request initiation | Web, Mobile, API |
| Gateway | Security, routing, rate limiting | Auth, SSL, Load Balancer |
| Orchestration | Agent state management, workflow | LangGraph, ReAct Agent |
| MCP Client | Protocol translation, streaming | HTTP Client, SSE Parser |
| External | Data and service integration | Restaurant APIs, Reviews |

---

## 3. Technical Stack

### 3.1 Core Technologies

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| Agent Framework | LangGraph | ^0.2.x | Graph-based agent orchestration |
| Agent Logic | LangChain | ^0.3.x | ReAct agent implementation |
| LLM Provider | OpenAI | GPT-4o | Natural language processing |
| Protocol | MCP | 1.0 | Server communication |
| Streaming | HTTP/2 + SSE | - | Real-time data flow |
| Runtime | Python | 3.11+ | Application runtime |
| Async | asyncio | - | Concurrent operations |
| Validation | Pydantic | 2.x | Data models |

### 3.2 Infrastructure Components

| Component | Technology | Purpose |
|-----------|------------|---------|
| API Gateway | FastAPI/Uvicorn | HTTP endpoints |
| Message Queue | Redis | Caching, pub/sub |
| Database | PostgreSQL | Persistent storage |
| Logging | ELK Stack | Observability |

---

## 4. MCP Server Integration Design

### 4.1 MCP Protocol Overview

The Model Context Protocol (MCP) defines how AI systems communicate with external servers. This design uses HTTP streaming (Server-Sent Events) for real-time communication.

### 4.2 MCP Connection Patterns

```python
# MCP Server Communication Flow
#
# 1. Initialize Connection
#    Client ──→ [MCP Initialize Request] ──→ Server
#    Client ←── [MCP Initialize Response] ──← Server
#
# 2. Tool Invocation (Streaming)
#    Client ──→ [Tool Call Request] ──→ Server
#    Client ←── [SSE Stream Start] ──← Server
#    Client ←── [Chunk 1] ──← Server
#    Client ←── [Chunk 2] ──← Server
#    ...
#    Client ←── [Done] ──← Server
#
# 3. Resource Access
#    Client ──→ [Resource Request] ──→ Server
#    Client ←── [Resource Response] ──← Server
```

### 4.3 MCP Client Implementation

```python
from typing import AsyncIterator, Optional
import asyncio
import sseclient
import json

class MCPClient:
    """MCP client with HTTP/SSE streaming support."""
    
    def __init__(self, server_url: str, api_key: Optional[str] = None):
        self.server_url = server_url
        self.api_key = api_key
        self.session: Optional[aiohttp.ClientSession] = None
        self.capabilities: dict = {}
        self._initialized = False
    
    async def initialize(self) -> dict:
        """Initialize MCP connection and negotiate capabilities."""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "1.0.0",
                "capabilities": {
                    "tools": {},
                    "resources": {},
                    "prompts": {}
                },
                "clientInfo": {
                    "name": "restaurant-agent",
                    "version": "1.0.0"
                }
            }
        }
        
        response = await self._send_request(request)
        self.capabilities = response.get("result", {}).get("capabilities", {})
        self._initialized = True
        return response
    
    async def call_tool_streaming(
        self, 
        tool_name: str, 
        arguments: dict
    ) -> AsyncIterator[dict]:
        """Call a tool with streaming response support."""
        if not self._initialized:
            await self.initialize()
        
        request = {
            "jsonrpc": "2.0",
            "id": self._generate_id(),
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        async for chunk in self._send_streaming_request(request):
            yield chunk
    
    async def _send_streaming_request(self, request: dict) -> AsyncIterator[dict]:
        """Send request and handle SSE streaming response."""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        async with self.session.post(
            f"{self.server_url}/mcp",
            json=request,
            headers=headers
        ) as response:
            response = await self._parse_sse_response(response)
            async for event in response.events():
                if event.event == "message":
                    data = json.loads(event.data)
                    if "result" in data:
                        yield data["result"]
                    elif "error" in data:
                        raise MCPError(data["error"])
    
    async def list_tools(self) -> list[dict]:
        """List available tools from MCP server."""
        request = {
            "jsonrpc": "2.0",
            "id": self._generate_id(),
            "method": "tools/list",
            "params": {}
        }
        response = await self._send_request(request)
        return response.get("result", {}).get("tools", [])
    
    async def list_resources(self) -> list[dict]:
        """List available resources from MCP server."""
        request = {
            "jsonrpc": "2.0",
            "id": self._generate_id(),
            "method": "resources/list",
            "params": {}
        }
        response = await self._send_request(request)
        return response.get("result", {}).get("resources", [])
    
    async def read_resource(self, uri: str) -> dict:
        """Read a specific resource from MCP server."""
        request = {
            "jsonrpc": "2.0",
            "id": self._generate_id(),
            "method": "resources/read",
            "params": {"uri": uri}
        }
        response = await self._send_request(request)
        return response.get("result", {})
    
    def _generate_id(self) -> int:
        """Generate unique request ID."""
        import time
        return int(time.time() * 1000)
    
    async def close(self):
        """Close MCP connection."""
        if self.session:
            await self.session.close()
```

### 4.4 MCP Server Pool Manager

```python
class MCPServerPool:
    """Manages multiple MCP server connections."""
    
    def __init__(self):
        self._servers: dict[str, MCPClient] = {}
        self._lock = asyncio.Lock()
    
    async def get_server(self, name: str, config: MCPConfig) -> MCPClient:
        """Get or create an MCP server connection."""
        async with self._lock:
            if name not in self._servers:
                client = MCPClient(
                    server_url=config.url,
                    api_key=config.api_key
                )
                await client.initialize()
                self._servers[name] = client
            return self._servers[name]
    
    async def close_all(self):
        """Close all MCP server connections."""
        for client in self._servers.values():
            await client.close()
        self._servers.clear()

@dataclass
class MCPConfig:
    """Configuration for an MCP server."""
    url: str
    api_key: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
```

---

## 5. LangGraph Agent Architecture

### 5.1 Graph Structure

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

# Define agent state
class AgentState(TypedDict):
    """State managed by LangGraph."""
    messages: Annotated[list[BaseMessage], add_messages]
    intent: Optional[str]
    entities: Optional[dict]
    search_results: Optional[list[Restaurant]]
    analysis_results: Optional[ReviewAnalysis]
    recommendation: Optional[Recommendation]
    reservation: Optional[Reservation]
    current_step: str
    error: Optional[str]
    user_preferences: Optional[UserPreferences]
```

### 5.2 Node Definitions

```python
# Graph nodes
async def intent_router(state: AgentState) -> AgentState:
    """Analyze user intent and route to appropriate handler."""
    messages = state["messages"]
    last_message = messages[-1]
    
    # Use LLM to classify intent
    intent_classifier = get_intent_classifier()
    intent_result = await intent_classifier.ainvoke(last_message)
    
    state["intent"] = intent_result.intent
    state["entities"] = intent_result.entities
    state["current_step"] = "intent_classified"
    
    return state

async def search_restaurants(state: AgentState) -> AgentState:
    """Handle restaurant search workflow."""
    entities = state.get("entities", {})
    mcp_client = get_mcp_client("restaurant")
    
    # Build search query
    query = RestaurantSearchQuery(
        cuisine=entities.get("cuisine"),
        location=entities.get("location"),
        price_range=entities.get("price_range"),
        rating_min=entities.get("rating_min"),
        keywords=entities.get("keywords")
    )
    
    # Search with streaming results
    results = []
    async for chunk in mcp_client.call_tool_streaming("search_restaurants", query.dict()):
        results.append(chunk)
        # Update state with incremental results
        state["search_results"] = results
    
    state["current_step"] = "search_completed"
    return state

async def analyze_reviews(state: AgentState) -> AgentState:
    """Handle review analysis workflow."""
    restaurant_id = state.get("entities", {}).get("restaurant_id")
    if not restaurant_id:
        state["error"] = "No restaurant specified for analysis"
        return state
    
    mcp_client = get_mcp_client("review")
    
    analysis_result = await mcp_client.call_tool_streaming(
        "analyze_reviews",
        {"restaurant_id": restaurant_id}
    )
    
    state["analysis_results"] = analysis_result
    state["current_step"] = "analysis_completed"
    return state

async def make_recommendation(state: AgentState) -> AgentState:
    """Generate personalized recommendations."""
    preferences = state.get("user_preferences")
    search_results = state.get("search_results", [])
    analysis = state.get("analysis_results")
    
    # Use LLM to generate recommendation
    recommender = get_recommendation_engine()
    recommendation = await recommender.ainvoke({
        "user_preferences": preferences,
        "restaurants": search_results,
        "analysis": analysis
    })
    
    state["recommendation"] = recommendation
    state["current_step"] = "recommendation_generated"
    return state

async def make_reservation(state: AgentState) -> AgentState:
    """Handle reservation workflow."""
    entities = state.get("entities", {})
    mcp_client = get_mcp_client("reservation")
    
    reservation_request = ReservationRequest(
        restaurant_id=entities.get("restaurant_id"),
        date=entities.get("date"),
        time=entities.get("time"),
        party_size=entities.get("party_size", 2),
        customer_name=entities.get("customer_name"),
        contact=entities.get("contact"),
        notes=entities.get("notes")
    )
    
    result = await mcp_client.call_tool_streaming(
        "create_reservation",
        reservation_request.dict()
    )
    
    state["reservation"] = result
    state["current_step"] = "reservation_completed"
    return state
```

### 5.3 Conditional Routing

```python
from langgraph.graph import StateGraph

def create_agent_graph() -> StateGraph:
    """Create the LangGraph agent workflow."""
    
    graph = StateGraph(AgentState)
    
    # Add nodes
    graph.add_node("intent_router", intent_router)
    graph.add_node("search_restaurants", search_restaurants)
    graph.add_node("analyze_reviews", analyze_reviews)
    graph.add_node("make_recommendation", make_recommendation)
    graph.add_node("make_reservation", make_reservation)
    graph.add_node("error_handler", error_handler)
    graph.add_node("generate_response", generate_response)
    
    # Set entry point
    graph.set_entry_point("intent_router")
    
    # Add conditional edges from intent router
    graph.add_conditional_edges(
        "intent_router",
        route_by_intent,
        {
            "search": "search_restaurants",
            "analyze": "analyze_reviews",
            "recommend": "make_recommendation",
            "reserve": "make_reservation",
            "unknown": "generate_response"
        }
    )
    
    # Add edges from search
    graph.add_edge("search_restaurants", "make_recommendation")
    graph.add_edge("make_recommendation", "generate_response")
    
    # Add edges from analyze
    graph.add_edge("analyze_reviews", "generate_response")
    
    # Add edges from reservation
    graph.add_edge("make_reservation", "generate_response")
    
    # Add error edge
    graph.add_edge("error_handler", "generate_response")
    
    # Add terminal edge
    graph.add_edge("generate_response", END)
    
    return graph.compile()

def route_by_intent(state: AgentState) -> str:
    """Route to appropriate handler based on intent."""
    intent = state.get("intent", "unknown")
    
    intent_mapping = {
        "search_restaurant": "search",
        "compare_restaurants": "search",
        "find_restaurants": "search",
        "analyze_reviews": "analyze",
        "get_reviews": "analyze",
        "recommend_restaurant": "recommend",
        "suggest_restaurant": "recommend",
        "make_reservation": "reserve",
        "book_table": "reserve",
        "reserve": "reserve"
    }
    
    return intent_mapping.get(intent, "unknown")
```

### 5.4 ReAct Agent Integration

```python
from langchain.agents import AgentExecutor, create_react_agent
from langchain_openai import ChatOpenAI
from langchain import hub

class ReActAgentWrapper:
    """Wraps LangChain ReAct agent for use in LangGraph."""
    
    def __init__(self, llm: ChatOpenAI, tools: list[BaseTool]):
        self.llm = llm
        self.tools = tools
        
        # Get ReAct prompt from hub
        prompt = hub.pull("hwchase17/react")
        
        # Create ReAct agent
        agent = create_react_agent(llm, tools, prompt)
        
        # Create executor
        self.executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            max_iterations=10,
            handle_parsing_errors=True
        )
    
    async def ainvoke(self, state: AgentState) -> AgentState:
        """Invoke ReAct agent with current state."""
        messages = state["messages"]
        
        # Convert messages to ReAct format
        input_text = self._format_messages(messages)
        
        # Execute agent
        result = await self.executor.ainvoke({"input": input_text})
        
        # Update state with agent output
        state["messages"].append(HumanMessage(content=result["output"]))
        
        return state
    
    def _format_messages(self, messages: list[BaseMessage]) -> str:
        """Format messages for ReAct agent."""
        # Implementation depends on message types
        return "\n".join([f"{m.type}: {m.content}" for m in messages])
```

---

## 6. ReAct Agent Tool Schema

### 6.1 Tool Definitions

```python
from langchain.tools import Tool
from pydantic import BaseModel, Field
from typing import Optional

# --- Search Tools ---

class RestaurantSearchInput(BaseModel):
    """Input for restaurant search."""
    query: str = Field(description="Search query text")
    location: Optional[str] = Field(None, description="City or neighborhood")
    cuisine: Optional[str] = Field(None, description="Cuisine type")
    price_range: Optional[str] = Field(None, description="Price range: $, $$, $$$, $$$$")
    rating_min: Optional[float] = Field(None, description="Minimum rating (0-5)")
    distance_max: Optional[int] = Field(None, description="Maximum distance in miles")
    limit: int = Field(10, description="Maximum results to return")

class RestaurantDetailInput(BaseModel):
    """Input for restaurant details."""
    restaurant_id: str = Field(description="Unique restaurant identifier")

# --- Analysis Tools ---

class ReviewAnalysisInput(BaseModel):
    """Input for review analysis."""
    restaurant_id: str = Field(description="Restaurant to analyze")
    source: Optional[str] = Field(None, description="Review source filter")
    date] = Field(None_from: Optional[str, description="Start date for reviews")
    date_to: Optional[str] = Field(None, description="End date for reviews")
    limit: int = Field(100, description="Maximum reviews to analyze")

class SentimentAnalysisInput(BaseModel):
    """Input for sentiment analysis."""
    text: str = Field(description="Text to analyze")

# --- Recommendation Tools ---

class RecommendationInput(BaseModel):
    """Input for recommendations."""
    preferences: dict = Field(description="User preferences")
    context: Optional[str] = Field(None, description="Additional context (occasion, etc.)")
    exclude: Optional[list[str]] = Field(None, description="Restaurant IDs to exclude")

# --- Reservation Tools ---

class ReservationInput(BaseModel):
    """Input for making a reservation."""
    restaurant_id: str = Field(description="Restaurant ID")
    date: str = Field(description="Date in YYYY-MM-DD format")
    time: str = Field(description="Time in HH:MM format (24-hour)")
    party_size: int = Field(2, description="Number of guests")
    customer_name: str = Field(description="Customer name")
    email: str = Field(description="Customer email")
    phone: str = Field(description="Customer phone")
    special_requests: Optional[str] = Field(None, description="Special requests")

class ReservationCancelInput(BaseModel):
    """Input for canceling a reservation."""
    reservation_id: str = Field(description="Reservation ID to cancel")

class ReservationListInput(BaseModel):
    """Input for listing reservations."""
    status: Optional[str] = Field(None, description="Filter by status")
    date_from: Optional[str] = Field(None, description="Start date")
    date_to: Optional[str] = Field(None, description="End date")
```

### 6.2 Tool Implementations

```python
# Create LangChain tools from MCP clients

def create_search_tools(mcp_pool: MCPServerPool) -> list[Tool]:
    """Create search-related tools."""
    
    async def search_restaurants_impl(input_str: str) -> str:
        """Search for restaurants."""
        parsed = RestaurantSearchInput.model_validate_json(input_str)
        client = await mcp_pool.get_server("restaurant", config)
        
        results = []
        async for chunk in client.call_tool_streaming("search", parsed.dict()):
            results.append(chunk)
        
        return format_restaurant_results(results)
    
    async def get_restaurant_detail_impl(input_str: str) -> str:
        """Get detailed restaurant information."""
        parsed = RestaurantDetailInput.model_validate_json(input_str)
        client = await mcp_pool.get_server("restaurant", config)
        
        result = await client.call_tool_streaming("get_details", parsed.dict())
        return format_restaurant_detail(result)
    
    return [
        Tool(
            name="search_restaurants",
            description="Search for restaurants by cuisine, location, price range, or rating",
            args_schema=RestaurantSearchInput,
            coroutine=search_restaurants_impl
        ),
        Tool(
            name="get_restaurant_details",
            description="Get detailed information about a specific restaurant",
            args_schema=RestaurantDetailInput,
            coroutine=get_restaurant_detail_impl
        )
    ]

def create_analysis_tools(mcp_pool: MCPServerPool) -> list[Tool]:
    """Create review analysis tools."""
    
    async def analyze_reviews_impl(input_str: str) -> str:
        """Analyze reviews for a restaurant."""
        parsed = ReviewAnalysisInput.model_validate_json(input_str)
        client = await mcp_pool.get_server("review", config)
        
        results = []
        async for chunk in client.call_tool_streaming("analyze", parsed.dict()):
            results.append(chunk)
        
        return format_analysis_results(results)
    
    async def get_sentiment_impl(input_str: str) -> str:
        """Analyze sentiment of text."""
        parsed = SentimentAnalysisInput.model_validate_json(input_str)
        client = await mcp_pool.get_server("review", config)
        
        result = await client.call_tool_streaming("sentiment", parsed.dict())
        return format_sentiment_result(result)
    
    return [
        Tool(
            name="analyze_reviews",
            description="Analyze reviews for a restaurant to get insights on food, service, ambiance, and value",
            args_schema=ReviewAnalysisInput,
            coroutine=analyze_reviews_impl
        ),
        Tool(
            name="analyze_sentiment",
            description="Analyze the sentiment of any text",
            args_schema=SentimentAnalysisInput,
            coroutine=get_sentiment_impl
        )
    ]

def create_reservation_tools(mcp_pool: MCPServerPool) -> list[Tool]:
    """Create reservation tools."""
    
    async def create_reservation_impl(input_str: str) -> str:
        """Make a restaurant reservation."""
        parsed = ReservationInput.model_validate_json(input_str)
        client = await mcp_pool.get_server("reservation", config)
        
        result = await client.call_tool_streaming("create", parsed.dict())
        return format_reservation_confirmation(result)
    
    async def cancel_reservation_impl(input_str: str) -> str:
        """Cancel an existing reservation."""
        parsed = ReservationCancelInput.model_validate_json(input_str)
        client = await mcp_pool.get_server("reservation", config)
        
        result = await client.call_tool_streaming("cancel", parsed.dict())
        return format_cancellation_result(result)
    
    async def list_reservations_impl(input_str: str) -> str:
        """List user's reservations."""
        parsed = ReservationListInput.model_validate_json(input_str)
        client = await mcp_pool.get_server("reservation", config)
        
        results = []
        async for chunk in client.call_tool_streaming("list", parsed.dict()):
            results.append(chunk)
        
        return format_reservation_list(results)
    
    return [
        Tool(
            name="create_reservation",
            description="Make a table reservation at a restaurant",
            args_schema=ReservationInput,
            coroutine=create_reservation_impl
        ),
        Tool(
            name="cancel_reservation",
            description="Cancel an existing reservation",
            args_schema=ReservationCancelInput,
            coroutine=cancel_reservation_impl
        ),
        Tool(
            name="list_reservations",
            description="List user's reservations",
            args_schema=ReservationListInput,
            coroutine=list_reservations_impl
        )
    ]

def create_recommendation_tools(mcp_pool: MCPServerPool) -> list[Tool]:
    """Create recommendation tools."""
    
    async def get_recommendations_impl(input_str: str) -> str:
        """Get personalized restaurant recommendations."""
        parsed = RecommendationInput.model_validate_json(input_str)
        client = await mcp_pool.get_server("recommendation", config)
        
        result = []
        async for chunk in client.call_tool_streaming("recommend", parsed.dict()):
            result.append(chunk)
        
        return format_recommendations(result)
    
    return [
        Tool(
            name="get_recommendations",
            description="Get personalized restaurant recommendations based on preferences",
            args_schema=RecommendationInput,
            coroutine=get_recommendations_impl
        )
    ]
```

---

## 7. Data Models

### 7.1 Core Domain Models

```python
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, list
from datetime import datetime, date
from enum import Enum

class PriceRange(str, Enum):
    """Price range enumeration."""
    BUDGET = "$"
    MODERATE = "$$"
    UPSCALE = "$$$"
    FINE_DINING = "$$$$"

class CuisineType(str, Enum):
    """Cuisine type enumeration."""
    ITALIAN = "italian"
    JAPANESE = "japanese"
    MEXICAN = "mexican"
    CHINESE = "chinese"
    INDIAN = "indian"
    AMERICAN = "american"
    FRENCH = "french"
    THAI = "thai"
    KOREAN = "korean"
    MEDITERRANEAN = "mediterranean"
    OTHER = "other"

class Restaurant(BaseModel):
    """Restaurant domain model."""
    id: str = Field(..., description="Unique restaurant identifier")
    name: str = Field(..., description="Restaurant name")
    description: Optional[str] = Field(None, description="Restaurant description")
    cuisine: list[CuisineType] = Field(..., description="Cuisine types")
    price_range: PriceRange = Field(..., description="Price range")
    rating: float = Field(..., ge=0, le=5, description="Average rating")
    review_count: int = Field(0, ge=0, description="Number of reviews")
    address: str = Field(..., description="Street address")
    city: str = Field(..., description="City")
    state: str = Field(..., description="State/province")
    zip_code: str = Field(..., description="ZIP/postal code")
    latitude: float = Field(..., description="Latitude")
    longitude: float = Field(..., description="Longitude")
    phone: Optional[str] = Field(None, description="Phone number")
    website: Optional[str] = Field(None, description="Website URL")
    hours: Optional[dict[str, str]] = Field(None, description="Operating hours")
    images: list[str] = Field(default_factory=list, description="Image URLs")
    features: list[str] = Field(default_factory=list, description="Features/amenities")

class Review(BaseModel):
    """Review domain model."""
    id: str = Field(..., description="Unique review identifier")
    restaurant_id: str = Field(..., description="Associated restaurant")
    source: str = Field(..., description="Review source (Yelp, Google, etc.)")
    author: str = Field(..., description="Review author")
    rating: float = Field(..., ge=0, le=5, description="Review rating")
    title: Optional[str] = Field(None, description="Review title")
    text: str = Field(..., description="Review text")
    date: date = Field(..., description="Review date")
    helpful_count: int = Field(0, description="Helpful votes")
    categories: list[str] = Field(default_factory=list, description="Review categories")

class ReviewAnalysis(BaseModel):
    """Review analysis result."""
    restaurant_id: str = Field(..., description="Restaurant analyzed")
    overall_sentiment: str = Field(..., description="Overall sentiment score")
    category_ratings: dict[str, float] = Field(..., description="Ratings by category")
    pros: list[str] = Field(default_factory=list, description="Common positives")
    cons: list[str] = Field(default_factory=list, description="Common negatives")
    highlights: list[str] = Field(default_factory=list, description="Key highlights")
    trend: Optional[str] = Field(None, description="Rating trend over time")

class UserPreferences(BaseModel):
    """User preferences for recommendations."""
    user_id: str = Field(..., description="User identifier")
    favorite_cuisines: list[CuisineType] = Field(default_factory=list)
    price_range_preference: Optional[PriceRange] = None
    dietary_restrictions: list[str] = Field(default_factory=list)
    preferred_location: Optional[str] = None
    min_rating: float = Field(0, ge=0, le=5)
    occasion: Optional[str] = None

class Recommendation(BaseModel):
    """Restaurant recommendation."""
    restaurant: Restaurant = Field(..., description="Recommended restaurant")
    score: float = Field(..., ge=0, le=1, description="Match score")
    reasons: list[str] = Field(..., description="Recommendation reasons")
    match_tags: list[str] = Field(default_factory=list, description="Matching preference tags")

class Reservation(BaseModel):
    """Reservation domain model."""
    id: str = Field(..., description="Unique reservation identifier")
    restaurant_id: str = Field(..., description="Restaurant ID")
    restaurant_name: str = Field(..., description="Restaurant name")
    user_id: str = Field(..., description="User ID")
    date: date = Field(..., description="Reservation date")
    time: str = Field(..., description="Reservation time")
    party_size: int = Field(..., ge=1, description="Number of guests")
    status: str = Field(..., description="Reservation status")
    customer_name: str = Field(..., description="Customer name")
    email: EmailStr = Field(..., description="Customer email")
    phone: str = Field(..., description="Customer phone")
    special_requests: Optional[str] = Field(None, description="Special requests")
    confirmation_code: str = Field(..., description="Confirmation code")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
```

---

## 8. Workflow Design

### 8.1 Restaurant Search Workflow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        SEARCH RESTAURANTS WORKFLOW                          │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌─────────┐
    │  User   │
    │ Query   │
    └────┬────┘
         │
         ▼
┌─────────────────────────┐
│   Intent Classification │
│  (Search/Compare/Find)  │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│    Entity Extraction    │
│  (Location, Cuisine,    │
│   Price, Rating, etc.)  │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  Build Search Query     │
│  (Validate & Enrich)    │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  MCP: search_restaurants│
│  (HTTP Stream)          │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  Receive Streaming      │
│  Results                │
│  ┌───────────────────┐  │
│  │ Restaurant 1     │  │
│  │ Restaurant 2     │  │
│  │ Restaurant 3     │  │
│  │ ...               │  │
│  └───────────────────┘  │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  Rank & Format Results │
│  (Score, Sort, Format) │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  Generate Response      │
│  (Natural Language)    │
└───────────┬─────────────┘
            │
            ▼
    ┌───────────────┐
    │ Return Results│
    └───────────────┘
```

### 8.2 Review Analysis Workflow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         REVIEW ANALYSIS WORKFLOW                             │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌─────────┐
    │  User   │
    │ Request │
    └────┬────┘
         │
         ▼
┌─────────────────────────┐
│  Validate Restaurant    │
│  (Exists & Active)      │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  Collect Reviews        │
│  (From Multiple APIs)   │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  MCP: analyze_reviews   │
│  (HTTP Stream)          │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  Process Results        │
│  • Sentiment Analysis   │
│  • Category Extraction  │
│  • Trend Detection      │
│  • Key Theme Discovery  │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  Generate Insights      │
│  (Natural Language)     │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  Format Response        │
│  (Structured + Summary) │
└───────────┬─────────────┘
            │
            ▼
    ┌───────────────┐
    │ Return Analysis│
    └───────────────┘
```

### 8.3 Recommendation Workflow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       RECOMMENDATION WORKFLOW                                │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌─────────┐
    │  User   │
    │ Request │
    └────┬────┘
         │
         ▼
┌─────────────────────────┐
│  Load User Preferences │
│  (From Profile/History) │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  Build Recommendation   │
│  Context                │
│  (Search Results +      │
│   Analysis + Preferences)│
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  MCP: get_recommendations│
│  (HTTP Stream)          │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  Score & Rank           │
│  (ML Model + Rules)     │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  Generate Reasons       │
│  (Explain Recommendations)│
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  Format Response        │
│  (With Reasoning)       │
└───────────┬─────────────┘
            │
            ▼
    ┌───────────────┐
    │ Return Results│
    └───────────────┘
```

### 8.4 Reservation Workflow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        RESERVATION WORKFLOW                                  │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌─────────┐
    │  User   │
    │ Request │
    └────┬────┘
         │
         ▼
┌─────────────────────────┐
│  Validate Reservation   │
│  Details                │
│  (Date, Time, Party Size│
│   Restaurant Available) │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  Check Availability     │
│  (Real-time)            │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  Confirm Details        │
│  (User Confirmation)    │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  MCP: create_reservation│
│  (HTTP Stream)          │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  Process Confirmation   │
│  (Get Confirmation Code)│
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  Send Notifications     │
│  (Email + SMS)          │
└───────────┬─────────────┘
            │
            ▼
    ┌───────────────┐
    │ Return Confirmation│
    └───────────────┘
```

---

## 9. API Design

### 9.1 REST API Endpoints

```python
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Restaurant Agent API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Chat/Agent Endpoints ---

@app.post("/api/v1/chat")
async def chat(
    request: ChatRequest,
    auth: Auth = Depends(get_auth)
) -> ChatResponse:
    """
    Main chat endpoint for agent interaction.
    Handles natural language requests for all agent capabilities.
    """
    # Process through LangGraph
    agent = get_agent()
    result = await agent.ainvoke({
        "messages": [HumanMessage(content=request.message)],
        "user_id": auth.user_id
    })
    
    return ChatResponse(
        message=result["messages"][-1].content,
        session_id=request.session_id,
        actions=result.get("actions")
    )

@app.post("/api/v1/chat/stream")
async def chat_stream(
    request: ChatRequest,
    auth: Auth = Depends(get_auth)
) -> StreamingResponse:
    """
    Streaming chat endpoint for real-time agent responses.
    Uses SSE for incremental updates.
    """
    async def event_generator():
        agent = get_agent()
        async for chunk in agent.astream({
            "messages": [HumanMessage(content=request.message)],
            "user_id": auth.user_id
        }):
            yield f"data: {json.dumps(chunk)}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )

# --- Search Endpoints ---

@app.post("/api/v1/restaurants/search")
async def search_restaurants(
    request: SearchRequest,
    auth: Auth = Depends(get_auth)
) -> SearchResponse:
    """Search for restaurants."""
    mcp_client = await mcp_pool.get_server("restaurant", config)
    
    results = []
    async for chunk in mcp_client.call_tool_streaming("search", request.dict()):
        results.append(chunk)
    
    return SearchResponse(
        restaurants=[Restaurant(**r) for r in results],
        total=len(results)
    )

@app.get("/api/v1/restaurants/{restaurant_id}")
async def get_restaurant(
    restaurant_id: str,
    auth: Auth = Depends(get_auth)
) -> RestaurantDetail:
    """Get detailed restaurant information."""
    mcp_client = await mcp_pool.get_server("restaurant", config)
    
    result = await mcp_client.call_tool_streaming(
        "get_details",
        {"restaurant_id": restaurant_id}
    )
    
    return RestaurantDetail(**result)

# --- Analysis Endpoints ---

@app.post("/api/v1/restaurants/{restaurant_id}/analyze")
async def analyze_restaurant(
    restaurant_id: str,
    request: AnalysisRequest,
    auth: Auth = Depends(get_auth)
) -> AnalysisResponse:
    """Analyze restaurant reviews."""
    mcp_client = await mcp_pool.get_server("review", config)
    
    results = []
    async for chunk in mcp_client.call_tool_streaming(
        "analyze",
        {"restaurant_id": restaurant_id, **request.dict()}
    ):
        results.append(chunk)
    
    return AnalysisResponse(**merge_results(results))

# --- Recommendation Endpoints ---

@app.post("/api/v1/recommendations")
async def get_recommendations(
    request: RecommendationRequest,
    auth: Auth = Depends(get_auth)
) -> RecommendationResponse:
    """Get personalized recommendations."""
    mcp_client = await mcp_pool.get_server("recommendation", config)
    
    results = []
    async for chunk in mcp_client.call_tool_streaming(
        "recommend",
        {**request.dict(), "user_id": auth.user_id}
    ):
        results.append(chunk)
    
    return RecommendationResponse(
        recommendations=[Recommendation(**r) for r in results]
    )

# --- Reservation Endpoints ---

@app.post("/api/v1/reservations")
async def create_reservation(
    request: ReservationRequest,
    auth: Auth = Depends(get_auth)
) -> ReservationResponse:
    """Create a new reservation."""
    mcp_client = await mcp_pool.get_server("reservation", config)
    
    result = await mcp_client.call_tool_streaming(
        "create",
        {**request.dict(), "user_id": auth.user_id}
    )
    
    return ReservationResponse(**result)

@app.get("/api/v1/reservations")
async def list_reservations(
    auth: Auth = Depends(get_auth),
    status: Optional[str] = None
) -> ReservationListResponse:
    """List user's reservations."""
    mcp_client = await mcp_pool.get_server("reservation", config)
    
    results = []
    async for chunk in mcp_client.call_tool_streaming(
        "list",
        {"user_id": auth.user_id, "status": status}
    ):
        results.append(chunk)
    
    return ReservationListResponse(
        reservations=[Reservation(**r) for r in results]
    )

@app.delete("/api/v1/reservations/{reservation_id}")
async def cancel_reservation(
    reservation_id: str,
    auth: Auth = Depends(get_auth)
) -> CancellationResponse:
    """Cancel a reservation."""
    mcp_client = await mcp_pool.get_server("reservation", config)
    
    result = await mcp_client.call_tool_streaming(
        "cancel",
        {"reservation_id": reservation_id, "user_id": auth.user_id}
    )
    
    return CancellationResponse(**result)

# --- User Preferences Endpoints ---

@app.get("/api/v1/preferences")
async def get_preferences(
    auth: Auth = Depends(get_auth)
) -> PreferencesResponse:
    """Get user preferences."""
    # Load from database
    preferences = await preferences_service.get(auth.user_id)
    return PreferencesResponse(**preferences.dict())

@app.put("/api/v1/preferences")
async def update_preferences(
    request: UpdatePreferencesRequest,
    auth: Auth = Depends(get_auth)
) -> PreferencesResponse:
    """Update user preferences."""
    preferences = await preferences_service.update(
        auth.user_id,
        request.preferences
    )
    return PreferencesResponse(**preferences.dict())
```

### 9.2 Request/Response Models

```python
from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    """Chat request model."""
    message: str = Field(..., min_length=1, max_length=4000)
    session_id: Optional[str] = None
    context: Optional[dict] = None

class ChatResponse(BaseModel):
    """Chat response model."""
    message: str
    session_id: str
    actions: Optional[list[dict]] = None
    data: Optional[dict] = None

class SearchRequest(BaseModel):
    """Restaurant search request."""
    query: str
    location: Optional[str] = None
    cuisine: Optional[str] = None
    price_range: Optional[str] = None
    rating_min: Optional[float] = None
    limit: int = 10

class SearchResponse(BaseModel):
    """Restaurant search response."""
    restaurants: list[Restaurant]
    total: int

class AnalysisRequest(BaseModel):
    """Review analysis request."""
    source: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    limit: int = 100

class AnalysisResponse(BaseModel):
    """Review analysis response."""
    restaurant_id: str
    sentiment: str
    category_ratings: dict[str, float]
    pros: list[str]
    cons: list[str]
    highlights: list[str]

class RecommendationRequest(BaseModel):
    """Recommendation request."""
    preferences: dict
    context: Optional[str] = None
    exclude: Optional[list[str]] = None

class RecommendationResponse(BaseModel):
    """Recommendation response."""
    recommendations: list[Recommendation]

class ReservationRequest(BaseModel):
    """Reservation request."""
    restaurant_id: str
    date: str
    time: str
    party_size: int = 2
    customer_name: str
    email: str
    phone: str
    special_requests: Optional[str] = None

class ReservationResponse(BaseModel):
    """Reservation response."""
    reservation: Reservation
    confirmation_code: str

class ReservationListResponse(BaseModel):
    """Reservation list response."""
    reservations: list[Reservation]

class CancellationResponse(BaseModel):
    """Cancellation response."""
    success: bool
    message: str
    reservation_id: str
```

---

## 10. Error Handling & Resilience

### 10.1 Error Types

```python
class AgentError(Exception):
    """Base exception for agent errors."""
    def __init__(self, message: str, code: str, details: dict = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)

class MCPConnectionError(AgentError):
    """MCP server connection error."""
    def __init__(self, server: str, details: dict = None):
        super().__init__(
            message=f"Failed to connect to MCP server: {server}",
            code="MCP_CONNECTION_ERROR",
            details=details
        )

class MCPTimeoutError(AgentError):
    """MCP request timeout."""
    def __init__(self, server: str, operation: str, timeout: int):
        super().__init__(
            message=f"MCP request timeout: {operation} on {server}",
            code="MCP_TIMEOUT",
            details={"server": server, "operation": operation, "timeout": timeout}
        )

class MCPStreamError(AgentError):
    """MCP streaming error."""
    def __init__(self, server: str, details: dict = None):
        super().__init__(
            message=f"MCP stream error from {server}",
            code="MCP_STREAM_ERROR",
            details=details
        )

class ValidationError(AgentError):
    """Input validation error."""
    def __init__(self, field: str, message: str):
        super().__init__(
            message=f"Validation error on {field}: {message}",
            code="VALIDATION_ERROR",
            details={"field": field}
        )

class ReservationError(AgentError):
    """Reservation-specific errors."""
    def __init__(self, message: str, code: str, details: dict = None):
        super().__init__(
            message=message,
            code=code,
            details=details
        )

class RestaurantNotFoundError(AgentError):
    """Restaurant not found."""
    def __init__(self, restaurant_id: str):
        super().__init__(
            message=f"Restaurant not found: {restaurant_id}",
            code="RESTAURANT_NOT_FOUND",
            details={"restaurant_id": restaurant_id}
        )
```

### 10.2 Error Handling Strategies

```python
from tenacity import retry, stop_after_attempt, wait_exponential
import logging

logger = logging.getLogger(__name__)

class MCPRetryHandler:
    """Handles retry logic for MCP operations."""
    
    def __init__(
        self,
        max_attempts: int = 3,
        min_wait: float = 1.0,
        max_wait: float = 10.0,
        multiplier: float = 2.0
    ):
        self.max_attempts = max_attempts
        self.min_wait = min_wait
        self.max_wait = max_wait
        self.multiplier = multiplier
    
    def with_retry(self, operation: str):
        """Decorator for retrying MCP operations."""
        return retry(
            stop=stop_after_attempt(self.max_attempts),
            wait=wait_exponential(
                multiplier=self.multiplier,
                min=self.min_wait,
                max=self.max_wait
            ),
            retry=lambda exc: isinstance(exc, (MCPConnectionError, MCPTimeoutError)),
            before_sleep=lambda retry_state: logger.warning(
                f"Retrying {operation} after {retry_state.attempt_number} attempts"
            )
        )

class ErrorHandler:
    """Central error handling for the agent."""
    
    @staticmethod
    async def handle_mcp_error(error: MCPError, context: dict) -> AgentState:
        """Handle MCP-related errors."""
        logger.error(f"MCP Error: {error.code} - {error.message}")
        
        # Try fallback MCP server if available
        if "fallback" in context:
            return await ErrorHandler._try_fallback(error, context)
        
        # Return error state
        return {
            "error": {
                "type": "mcp_error",
                "code": error.code,
                "message": error.message,
                "recoverable": ErrorHandler._is_recoverable(error)
            },
            "current_step": "error_handled"
        }
    
    @staticmethod
    def _is_recoverable(error: MCPError) -> bool:
        """Determine if error is recoverable."""
        recoverable_codes = [
            "MCP_CONNECTION_ERROR",
            "MCP_TIMEOUT",
            "MCP_STREAM_ERROR"
        ]
        return error.code in recoverable_codes
    
    @staticmethod
    async def handle_validation_error(error: ValidationError) -> AgentState:
        """Handle validation errors."""
        return {
            "error": {
                "type": "validation_error",
                "field": error.details.get("field"),
                "message": error.message
            },
            "current_step": "error_handled"
        }

# Circuit breaker for MCP servers
class MCPCircuitBreaker:
    """Circuit breaker for MCP server failures."""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        half_open_requests: int = 3
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_requests = half_open_requests
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open
    
    def record_success(self):
        """Record successful request."""
        self.failure_count = 0
        self.state = "closed"
    
    def record_failure(self):
        """Record failed request."""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "open"
            logger.warning(f"Circuit breaker opened for MCP server")
    
    def can_execute(self) -> bool:
        """Check if request can be executed."""
        if self.state == "closed":
            return True
        
        if self.state == "open":
            if self._should_attempt_reset():
                self.state = "half-open"
                return True
            return False
        
        # half-open state
        return True
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if not self.last_failure_time:
            return True
        
        elapsed = (datetime.utcnow() - self.last_failure_time).seconds
        return elapsed >= self.recovery_timeout
```

---

## 11. Security Considerations

### 11.1 Authentication & Authorization

```python
from fastapi import Security, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime, timedelta

security = HTTPBearer()

class AuthService:
    """Authentication service."""
    
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
    
    def verify_token(self, token: str) -> dict:
        """Verify JWT token."""
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            
            # Check expiration
            exp = payload.get("exp")
            if exp and datetime.fromtimestamp(exp) < datetime.utcnow():
                raise HTTPException(status_code=401, detail="Token expired")
            
            return payload
        
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
    
    def create_token(self, user_id: str, expires_in: int = 3600) -> str:
        """Create JWT token."""
        payload = {
            "user_id": user_id,
            "exp": datetime.utcnow() + timedelta(seconds=expires_in),
            "iat": datetime.utcnow()
        }
        
        return jwt.encode(
            payload,
            self.secret_key,
            algorithm=self.algorithm
        )

async def get_auth(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> Auth:
    """Dependency for authentication."""
    auth_service = get_auth_service()
    payload = auth_service.verify_token(credentials.credentials)
    
    return Auth(
        user_id=payload["user_id"],
        email=payload.get("email"),
        roles=payload.get("roles", [])
    )
```

### 11.2 API Key Management

```python
class APIKeyManager:
    """Manage API keys for MCP servers."""
    
    def __init__(self, vault_url: str, role: str):
        self.vault_url = vault_url
        self.role = role
        self._cache: dict[str, str] = {}
    
    async def get_api_key(self, server_name: str) -> str:
        """Get API key for MCP server."""
        if server_name in self._cache:
            return self._cache[server_name]
        
        # Fetch from secure vault
        key = await self._fetch_from_vault(server_name)
        self._cache[server_name] = key
        return key
    
    async def rotate_api_key(self, server_name: str) -> str:
        """Rotate API key for MCP server."""
        new_key = await self._rotate_in_vault(server_name)
        self._cache[server_name] = new_key
        return new_key
```

### 11.3 Input Sanitization

```python
import re
from html import escape

class InputSanitizer:
    """Sanitize user inputs."""
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 1000) -> str:
        """Sanitize string input."""
        # Remove control characters
        sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', value)
        # Escape HTML
        sanitized = escape(sanitized)
        # Limit length
        return sanitized[:max_length]
    
    @staticmethod
    def sanitize_email(email: str) -> str:
        """Sanitize and validate email."""
        email = email.lower().strip()
        # Basic email validation regex
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise ValidationError("email", "Invalid email format")
        return email
    
    @staticmethod
    def sanitize_phone(phone: str) -> str:
        """Sanitize phone number."""
        # Remove all non-digit characters
        return re.sub(r'\D', '', phone)
```

---

## 12. Implementation Roadmap

### 12.1 Phased Implementation

| Phase | Description | Duration | Deliverables |
|-------|-------------|----------|---------------|
| **Phase 1: Foundation** | Core infrastructure and MCP integration | 3 weeks | - MCP client implementation<br>- Basic agent state<br>- Error handling |
| **Phase 2: Search** | Restaurant search functionality | 2 weeks | - Search endpoints<br>- Restaurant data models<br>- Basic ranking |
| **Phase 3: Analysis** | Review analysis features | 2 weeks | - Analysis tools<br>- Sentiment analysis<br>- Trend detection |
| **Phase 4: Recommendations** | Recommendation engine | 2 weeks | - Preference management<br>- ML-based recommendations<br>- Explanation generation |
| **Phase 5: Reservations** | Booking functionality | 2 weeks | - Reservation endpoints<br>- Availability checking<br>- Confirmation flow |
| **Phase 6: Integration** | Full system integration | 2 weeks | - End-to-end testing<br>- Performance optimization<br>- Documentation |

### 12.2 Technical Milestones

```
Phase 1: Foundation (Weeks 1-3)
├── Week 1: Infrastructure Setup
│   ├── Set up FastAPI application
│   ├── Configure logging and monitoring
│   └── Set up development environment
├── Week 2: MCP Client Implementation
│   ├── Implement MCP client with HTTP/SSE
│   ├── Create connection pooling
│   └── Add retry and circuit breaker logic
└── Week 3: Basic LangGraph Agent
    ├── Define agent state schema
    ├── Create basic graph structure
    └── Implement error handling

Phase 2: Search (Weeks 4-5)
├── Week 4: Search API Development
│   ├── Implement restaurant search endpoint
│   ├── Create search query builder
│   └── Add result pagination
└── Week 5: Search Enhancement
    ├── Add advanced filtering
    ├── Implement ranking algorithm
    └── Add search suggestions

Phase 3: Analysis (Weeks 6-7)
├── Week 6: Review Collection
│   ├── Implement review aggregation
│   ├── Create data pipelines
│   └── Add review normalization
└── Week 7: Analysis Engine
    ├── Implement sentiment analysis
    ├── Add category extraction
    └── Create trend detection

Phase 4: Recommendations (Weeks 8-9)
├── Week 8: Recommendation System
│   ├── Build user preference model
    ├── Implement recommendation algorithm
    └── Add explanation generation
└── Week 9: Personalization
    ├── Add collaborative filtering
    ├── Implement A/B testing framework
    └── Add feedback loop

Phase 5: Reservations (Weeks 10-11)
├── Week 10: Booking System
│   ├── Implement reservation endpoint
│   ├── Add availability checking
    └── Create confirmation flow
└── Week 11: Reservation Management
    ├── Add modification features
    ├── Implement cancellation
    └── Add notifications

Phase 6: Integration (Weeks 12-13)
├── Week 12: Integration Testing
│   ├── End-to-end testing
│   ├── Load testing
│   └── Security testing
└── Week 13: Deployment
    ├── CI/CD pipeline setup
    ├── Production deployment
    └── Documentation
```

---

## 13. Alternatives & Trade-offs

### 13.1 Architecture Alternatives

| Alternative | Pros | Cons | Recommendation |
|-------------|------|------|----------------|
| **GraphQL over REST** | Flexible queries, single endpoint | More complex setup, potential over-fetching | Use REST for simplicity; GraphQL as future enhancement |
| **WebSocket over SSE** | Bidirectional, lower latency | More complex connection management | Use SSE for server-initiated streams; WebSocket for future real-time features |
| **Single MCP Server** | Simpler deployment | Single point of failure, harder to scale | Use multiple MCP servers with pool for resilience |
| **Stateless Agent** | Easier scaling | No conversation context | Use LangGraph state for conversation context; scale with distributed cache |

### 13.2 Technology Alternatives

| Component | Alternative | Comparison |
|-----------|------------|------------|
| **LLM Provider** | Anthropic Claude | Similar capabilities; consider for cost optimization |
| **Agent Framework** | AutoGen | Better for multi-agent; LangGraph chosen for fine-grained control |
| **Streaming** | Webhooks | Less efficient for real-time; SSE preferred |
| **Database** | MongoDB | Good for flexible schemas; PostgreSQL chosen for relational data |

### 13.3 Design Decisions Rationale

1. **LangGraph over Custom Agent**
   - **Decision**: Use LangGraph for agent orchestration
   - **Rationale**: Built-in state management, visual debugging, human-in-the-loop support
   - **Alternative considered**: Custom implementation using asyncio

2. **HTTP/SSE for MCP**
   - **Decision**: Use HTTP with Server-Sent Events for streaming
   - **Rationale**: Native browser support, simple implementation, works well with firewalls
   - **Alternative considered**: WebSocket for bidirectional streaming

3. **ReAct Agent Pattern**
   - **Decision**: Use ReAct (Reasoning + Acting) pattern
   - **Rationale**: Proven effectiveness for tool-use agents, good interpretability
   - **Alternative considered**: Chain-of-Thought for simpler tasks

4. **Sub-Agent Architecture**
   - **Decision**: Use specialized sub-agents for each domain
   - **Rationale**: Better domain specialization, easier to maintain, clearer separation of concerns
   - **Alternative considered**: Single monolithic agent

### 13.4 Scalability Considerations

| Component | Current Design | Scaling Strategy |
|-----------|---------------|------------------|
| **API Gateway** | Single instance | Add load balancer, auto-scaling |
| **LangGraph Agent** | Single instance | Use Redis for state sharing |
| **MCP Clients** | Connection pool | Add MCP server replicas |
| **Database** | Single PostgreSQL | Read replicas, sharding |
| **Caching** | In-memory | Distributed Redis cluster |

### 13.5 Future Enhancements

| Enhancement | Description | Priority |
|-------------|-------------|----------|
| **Multi-language Support** | Support multiple languages for reviews and responses | High |
| **Voice Interface** | Add voice input/output capability | Medium |
| **Image Analysis** | Analyze restaurant photos using vision models | Medium |
| **Advanced Analytics** | Dashboard for restaurant insights | Low |
| **Social Features** | Share recommendations, friend lists | Low |

---

## Appendix A: Configuration Schema

```yaml
# config.yaml
application:
  name: restaurant-agent
  version: 1.0.0
  environment: development  # development, staging, production

server:
  host: 0.0.0.0
  port: 8000
  workers: 4
  timeout: 60

llm:
  provider: openai
  model: gpt-4o
  temperature: 0.7
  max_tokens: 2000

mcp_servers:
  restaurant:
    url: https://api.restaurant-mcp.example.com
    timeout: 30
    max_retries: 3
  review:
    url: https://api.review-mcp.example.com
    timeout: 30
    max_retries: 3
  reservation:
    url: https://api.reservation-mcp.example.com
    timeout: 30
    max_retries: 3
  recommendation:
    url: https://api.recommendation-mcp.example.com
    timeout: 30
    max_retries: 3

database:
  host: localhost
  port: 5432
  name: restaurant_agent
  pool_size: 10
  max_overflow: 20

redis:
  host: localhost
  port: 6379
  db: 0

auth:
  jwt_secret: ${JWT_SECRET}
  jwt_algorithm: HS256
  token_expiry: 3600

logging:
  level: INFO
  format: json
  output: stdout

monitoring:
  enabled: true
  service_name: restaurant-agent
```

---

## Appendix B: API Examples

### Search Restaurants

```bash
curl -X POST "http://localhost:8000/api/v1/restaurants/search" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Italian restaurants",
    "location": "San Francisco",
    "price_range": "$$",
    "rating_min": 4.0,
    "limit": 10
  }'
```

### Analyze Reviews

```bash
curl -X POST "http://localhost:8000/api/v1/restaurants/rest_123/analyze" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "limit": 50
  }'
```

### Make Reservation

```bash
curl -X POST "http://localhost:8000/api/v1/reservations" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "restaurant_id": "rest_123",
    "date": "2026-03-20",
    "time": "19:00",
    "party_size": 4,
    "customer_name": "John Doe",
    "email": "john@example.com",
    "phone": "5551234567",
    "special_requests": "Window seat preferred"
  }'
```

### Chat with Agent

```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Find me a good Italian restaurant in SF for a romantic dinner",
    "session_id": "sess_abc123"
  }'
```

---

*Document Version: 1.0*  
*Last Updated: 2026-03-12*  
*Author: AI Agent Framework Design Team*
