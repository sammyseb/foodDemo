"""Chat service."""

import uuid
from typing import AsyncIterator, Dict, Any

from clients.agent_client import get_agent_client


class ChatService:
    """Service for handling chat requests."""
    
    def __init__(self):
        self.agent_client = get_agent_client()
    
    async def process_message(
        self,
        message: str,
        session_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """Process a chat message (non-streaming)."""
        result = await self.agent_client.chat_simple(
            message=message,
            session_id=session_id,
            user_id=user_id
        )
        return result
    
    async def process_message_stream(
        self,
        message: str,
        session_id: str,
        user_id: str
    ) -> AsyncIterator[Dict[str, Any]]:
        """Process a chat message with streaming response."""
        async for chunk in self.agent_client.chat(
            message=message,
            session_id=session_id,
            user_id=user_id
        ):
            yield chunk
    
    @staticmethod
    def create_session_id() -> str:
        """Create a new session ID."""
        return str(uuid.uuid4())
