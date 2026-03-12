"""Search agent for restaurant search."""

from typing import Any, Dict, List

from langchain.prompts import ChatPromptTemplate
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_openai import ChatOpenAI

from .base import BaseAgent


# Search agent system prompt
SEARCH_PROMPT = """You are a restaurant search specialist.

Your job is to help users find restaurants using the available tools.

Available tools:
- search_restaurants: Search for restaurants by query, location, cuisine, price
- get_restaurant_details: Get detailed information about a specific restaurant

Guidelines:
1. Always use search_restaurants first to find options
2. Present results clearly with name, rating, price range, location
3. Ask follow-up questions if user preferences are unclear
4. Use get_restaurant_details when user wants more info about a specific place

When presenting results:
- Restaurant Name
- Rating (stars)
- Price Range ($-$$$$)
- Location/Address
- Cuisine Type

Be friendly and helpful!"""


class SearchAgent(BaseAgent):
    """
    Search agent that helps users find restaurants.
    
    This agent uses tools to search for restaurants and present
    results to the user in a helpful format.
    """
    
    def __init__(self, llm: ChatOpenAI, tools: List[Any]):
        super().__init__(
            llm=llm,
            tools=tools,
            system_prompt=SEARCH_PROMPT,
            max_iterations=10
        )
    
    async def ainvoke(
        self, 
        input_text: str, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Search for restaurants based on user input.
        
        Args:
            input_text: The user's search request
            context: Additional context including entities from router
            
        Returns:
            Dict with 'response' and 'tool_outputs'
        """
        # Enhance input with context from router
        enhanced_input = self._enhance_input(input_text, context)
        
        # Create prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", "{input}")
        ])
        
        # Create agent with tools
        agent = create_tool_calling_agent(self.llm, self.tools, prompt)
        executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            max_iterations=self.max_iterations,
            handle_parsing_errors="I couldn't find restaurants matching your criteria. Please try a different search."
        )
        
        # Execute
        result = await executor.ainvoke({"input": enhanced_input})
        
        # Extract tool outputs and response
        tool_outputs = []
        if "tool_outputs" in result:
            for output in result["tool_outputs"]:
                if isinstance(output, dict):
                    tool_outputs.append(output)
        
        return {
            "response": result.get("output", ""),
            "tool_outputs": tool_outputs
        }
    
    async def astream(
        self, 
        input_text: str, 
        context: Dict[str, Any]
    ):
        """Stream search results."""
        # First yield the intent info if available
        if "entities" in context:
            yield {"type": "entities", "data": context["entities"]}
        
        # Stream the result
        result = await self.ainvoke(input_text, context)
        
        # Yield content
        yield {"type": "content", "text": result["response"]}
        
        # Yield tool outputs if any
        if result.get("tool_outputs"):
            yield {"type": "actions", "data": result["tool_outputs"]}
    
    def _enhance_input(self, input_text: str, context: Dict[str, Any]) -> str:
        """
        Enhance the search input with context from the router.
        
        Adds location, cuisine, and other preferences from the
        router's entity extraction to the search query.
        """
        entities = context.get("entities", {})
        
        if not entities:
            return input_text
        
        # Build enhanced query
        parts = [input_text]
        
        if "location" in entities:
            parts.append(f"in {entities['location']}")
        
        if "cuisine" in entities:
            parts.append(f"for {entities['cuisine']}")
        
        if "price_range" in entities:
            parts.append(f"at price range {entities['price_range']}")
        
        if "rating_min" in entities:
            parts.append(f"with rating {entities['rating_min']}+")
        
        return " ".join(parts)
