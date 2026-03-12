"""Agent client for communicating with the LangGraph agent service."""

import json
from typing import AsyncIterator, Optional

import aiohttp

from app.config import settings


class AgentClient:
    """Client for communicating with the LangGraph agent service."""
    
    def __init__(self, agent_url: Optional[str] = None):
        self.agent_url = agent_url or settings.agent_url
    
    async def chat(
        self,
        message: str,
        session_id: str,
        user_id: str
    ) -> AsyncIterator[dict]:
        """Stream chat response from agent."""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.agent_url}/agent/chat/stream",
                json={
                    "message": message,
                    "session_id": session_id,
                    "user_id": user_id
                }
            ) as response:
                async for line in response.content:
                    if line:
                        try:
                            data = json.loads(line)
                            yield data
                        except json.JSONDecodeError:
                            continue
    
    async def chat_simple(
        self,
        message: str,
        session_id: str,
        user_id: str
    ) -> dict:
        """Send chat message and get single response."""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.agent_url}/agent/chat",
                json={
                    "message": message,
                    "session_id": session_id,
                    "user_id": user_id
                }
            ) as response:
                return await response.json()


# Singleton instance
_agent_client: Optional[AgentClient] = None


def get_agent_client() -> AgentClient:
    """Get or create agent client singleton."""
    global _agent_client
    if _agent_client is None:
        _agent_client = AgentClient()
    return _agent_client
