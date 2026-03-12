"""Chat router."""

import json
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse

from dependencies.auth import CurrentUser, get_current_user
from dependencies.rate_limit import limiter
from models.request import ChatRequest
from models.response import ChatResponse
from services.chat_service import ChatService

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
@limiter.limit("60/minute")
async def chat(
    request: Request,
    chat_request: ChatRequest,
    current_user: CurrentUser = Depends(get_current_user)
):
    """Non-streaming chat endpoint."""
    service = ChatService()
    
    session_id = chat_request.session_id or service.create_session_id()
    
    result = await service.process_message(
        message=chat_request.message,
        session_id=session_id,
        user_id=current_user.id
    )
    
    return ChatResponse(
        message=result.get("message", ""),
        session_id=session_id,
        intent=result.get("intent"),
        entities=result.get("entities")
    )


@router.post("/chat/stream")
@limiter.limit("60/minute")
async def chat_stream(
    request: Request,
    chat_request: ChatRequest,
    current_user: CurrentUser = Depends(get_current_user)
):
    """Streaming chat endpoint with SSE."""
    service = ChatService()
    session_id = chat_request.session_id or service.create_session_id()
    
    async def event_generator():
        yield f"data: {json.dumps({'type': 'session_id', 'session_id': session_id})}\n\n"
        
        try:
            async for chunk in service.process_message_stream(
                message=chat_request.message,
                session_id=session_id,
                user_id=current_user.id
            ):
                yield f"data: {json.dumps(chunk)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
        
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )
