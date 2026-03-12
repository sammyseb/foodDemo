"""Router agent for intent classification."""

import json
import re
from typing import Any, Dict

from langchain.prompts import ChatPromptTemplate
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_openai import ChatOpenAI

from .base import BaseAgent


# Router system prompt
ROUTER_PROMPT = """You are a restaurant assistant router. 
Analyze the user's message and determine their intent:

INTENTS:
- search: Looking for restaurants (find, search, recommend, suggest)
- details: Want specific restaurant information (hours, menu, address)
- reserve: Want to make a reservation (book, reserve, table)
- recommend: Want personalized recommendations based on preferences
- compare: Want to compare restaurants
- chat: General conversation or greeting

Extract any entities from the message:
- location: City, neighborhood, address (e.g., "in San Francisco", "near downtown")
- cuisine: Type of food (e.g., "italian", "japanese", "mexican")
- price_range: Budget ($, $$, $$$, $$$$ or "cheap", "moderate", "expensive")
- rating: Minimum rating (e.g., "4 stars", "rating above 4")
- date: Reservation date (e.g., "tonight", "tomorrow", "next Friday")
- time: Reservation time (e.g., "7pm", "7:30")
- party_size: Number of guests (e.g., "for 4", "2 people")

IMPORTANT: Always respond with valid JSON in this exact format:
{{"intent": "search", "entities": {{"location": "San Francisco", "cuisine": "italian"}}}}"""


class RouterAgent(BaseAgent):
    """
    Router agent that classifies user intent and extracts entities.
    
    This agent analyzes the user's message to determine what they want
    (search, details, reserve, etc.) and extracts relevant information
    like location, cuisine, date, etc.
    """
    
    def __init__(self, llm: ChatOpenAI):
        super().__init__(
            llm=llm,
            tools=[],  # Router uses LLM reasoning only, no tools
            system_prompt=ROUTER_PROMPT,
            max_iterations=3
        )
    
    async def ainvoke(
        self, 
        input_text: str, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Classify intent and extract entities from user input.
        
        Args:
            input_text: The user's message
            context: Additional context (unused for router)
            
        Returns:
            Dict with 'intent' and 'entities' keys
        """
        # Create prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", "{input}")
        ])
        
        # Create agent without tools
        agent = create_tool_calling_agent(self.llm, [], prompt)
        executor = AgentExecutor(
            agent=agent,
            tools=[],
            verbose=False,
            handle_parsing_errors=True
        )
        
        # Execute
        result = await executor.ainvoke({"input": input_text})
        
        # Parse response
        return self._parse_response(result.get("output", ""))
    
    async def astream(
        self, 
        input_text: str, 
        context: Dict[str, Any]
    ):
        """Stream router results."""
        result = await self.ainvoke(input_text, context)
        yield {"type": "intent", "data": result}
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """
        Parse intent and entities from LLM response.
        
        Tries to extract JSON from the response. Falls back to
        keyword-based classification if JSON parsing fails.
        """
        # Try to find JSON in response
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        
        if json_match:
            try:
                parsed = json.loads(json_match.group())
                return {
                    "intent": parsed.get("intent", "chat"),
                    "entities": parsed.get("entities", {})
                }
            except json.JSONDecodeError:
                pass
        
        # Fallback: keyword-based classification
        return self._fallback_parse(response)
    
    def _fallback_parse(self, response: str) -> Dict[str, Any]:
        """Fallback keyword-based intent classification."""
        response_lower = response.lower()
        
        # Detect intent from keywords
        intent = "chat"
        
        search_keywords = ["find", "search", "look for", "recommend", "suggest", "best"]
        details_keywords = ["details", "info", "hours", "menu", "address", "phone"]
        reserve_keywords = ["book", "reserve", "reservation", "table", "seating"]
        
        if any(kw in response_lower for kw in reserve_keywords):
            intent = "reserve"
        elif any(kw in response_lower for kw in details_keywords):
            intent = "details"
        elif any(kw in response_lower for kw in search_keywords):
            intent = "search"
        
        # Try to extract entities from the original response
        entities = {}
        
        # Location patterns
        location_patterns = [
            r'in\s+([A-Za-z\s]+?)(?:\s|$|\.|,)',
            r'near\s+([A-Za-z\s]+?)(?:\s|$|\.|,)',
            r'around\s+([A-Za-z\s]+?)(?:\s|$|\.|,)',
        ]
        for pattern in location_patterns:
            match = re.search(pattern, response, re.IGNORECASE)
            if match:
                entities["location"] = match.group(1).strip()
                break
        
        # Cuisine patterns
        cuisines = ["italian", "mexican", "japanese", "chinese", "indian", 
                    "thai", "french", "american", "korean", "vietnamese"]
        for cuisine in cuisines:
            if cuisine in response_lower:
                entities["cuisine"] = cuisine
                break
        
        return {"intent": intent, "entities": entities}
