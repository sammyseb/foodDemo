"""FastAPI application for the Restaurant Agent."""

import uuid
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json
import logging

from app.config import get_settings
from agents.factory import AgentFactory
from graph.builder import create_agent_graph, create_initial_state

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Application state
class AppState:
    """Application state."""
    
    def __init__(self):
        self.settings = get_settings()
        self.factory: Optional[AgentFactory] = None
        self.graph = None
    
    def initialize(self):
        """Initialize the agents."""
        logger.info("Initializing Restaurant Agent...")
        
        # Create factory
        self.factory = AgentFactory(self.settings)
        
        # Create agents
        router = self.factory.create_router()
        search = self.factory.create_search()
        llm = self.factory.llm
        
        # Create graph
        self.graph = create_agent_graph(router, search, llm)
        
        logger.info("Restaurant Agent initialized!")


# Create app state
app_state = AppState()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown."""
    # Startup
    app_state.initialize()
    yield
    # Shutdown
    logger.info("Shutting down Restaurant Agent...")


# Create FastAPI app
app = FastAPI(
    title="Restaurant Agent API",
    description="AI-powered restaurant assistant using LangGraph",
    version="1.0.0",
    lifespan=lifespan
)


# Request/Response models
class ChatRequest(BaseModel):
    """Chat request model."""
    
    message: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Chat response model."""
    
    message: str
    session_id: str
    intent: Optional[str] = None
    entities: Optional[dict] = None


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "restaurant-agent"
    }


@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint."""
    return {"status": "ready"}


# Chat endpoints
@app.post("/agent/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Non-streaming chat endpoint.
    
    Send a message and get a response.
    """
    # Get or create session
    session_id = request.session_id or str(uuid.uuid4())
    user_id = request.user_id or "anonymous"
    
    # Create initial state
    initial_state = create_initial_state(
        message=request.message,
        session_id=session_id,
        user_id=user_id,
        router_agent=app_state.factory.create_router(),
        search_agent=app_state.factory.create_search(),
        llm=app_state.factory.llm
    )
    
    try:
        # Execute the graph
        result = await app_state.graph.ainvoke(initial_state)
        
        return ChatResponse(
            message=result.get("final_response", ""),
            session_id=session_id,
            intent=result.get("intent"),
            entities=result.get("entities")
        )
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agent/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Streaming chat endpoint.
    
    Send a message and get a streaming response using SSE.
    """
    # Get or create session
    session_id = request.session_id or str(uuid.uuid4())
    user_id = request.user_id or "anonymous"
    
    async def event_generator():
        # Send session ID first
        yield f"data: {json.dumps({'type': 'session_id', 'session_id': session_id})}\n\n"
        
        try:
            # Create initial state
            initial_state = create_initial_state(
                message=request.message,
                session_id=session_id,
                user_id=user_id,
                router_agent=app_state.factory.create_router(),
                search_agent=app_state.factory.create_search(),
                llm=app_state.factory.llm
            )
            
            # Stream results
            async for chunk in app_state.graph.astream(initial_state):
                # Stream intent
                if "intent" in chunk and chunk.get("intent"):
                    yield f"data: {json.dumps({'type': 'intent', 'data': {'intent': chunk['intent'], 'entities': chunk.get('entities', {})}})}\n\n"
                
                # Stream content
                if "final_response" in chunk and chunk["final_response"]:
                    yield f"data: {json.dumps({'type': 'content', 'text': chunk['final_response']})}\n\n"
                
                # Stream tool outputs
                if "tool_outputs" in chunk and chunk["tool_outputs"]:
                    yield f"data: {json.dumps({'type': 'actions', 'data': chunk['tool_outputs']})}\n\n"
                    
        except Exception as e:
            logger.error(f"Error in chat stream: {e}")
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
        
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


# Run the app
if __name__ == "__main__":
    import uvicorn
    
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
