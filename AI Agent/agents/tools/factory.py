"""Factory for creating tools."""

from typing import List

from langchain.tools import Tool

from .mcp_wrapper import MCPToolWrapper, MockMCPToolWrapper


class ToolFactory:
    """
    Factory for creating LangChain tools.
    
    Creates tools that connect to MCP servers or use mock data.
    """
    
    def __init__(
        self, 
        mcp_server_url: str = "http://localhost:8002",
        mcp_api_key: str = "",
        use_mock: bool = False
    ):
        self.mcp_server_url = mcp_server_url
        self.mcp_api_key = mcp_api_key
        self.use_mock = use_mock
    
    def create_search_tools(self) -> List[Tool]:
        """Create restaurant search tools."""
        
        if self.use_mock:
            return self._create_mock_tools()
        
        return self._create_mcp_tools()
    
    def _create_mcp_tools(self) -> List[Tool]:
        """Create MCP-based tools."""
        
        # Search restaurants tool
        search_tool = MCPToolWrapper(
            name="search_restaurants",
            description="Search for restaurants by query, location, cuisine, price range, or rating. Input should be a JSON string with fields like: query, location, cuisine, radius, limit.",
            mcp_server_url=self.mcp_server_url,
            mcp_tool_name="search_restaurants",
            api_key=self.mcp_api_key,
            input_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "location": {"type": "string"},
                    "cuisine": {"type": "string"},
                    "radius": {"type": "integer"},
                    "limit": {"type": "integer"}
                }
            }
        )
        
        # Get restaurant details tool
        details_tool = MCPToolWrapper(
            name="get_restaurant_details",
            description="Get detailed information about a specific restaurant by its place ID. Input should be a JSON string with field: place_id.",
            mcp_server_url=self.mcp_server_url,
            mcp_tool_name="get_place_details",
            api_key=self.mcp_api_key,
            input_schema={
                "type": "object",
                "properties": {
                    "place_id": {"type": "string"}
                }
            }
        )
        
        # Get reviews tool
        reviews_tool = MCPToolWrapper(
            name="get_restaurant_reviews",
            description="Get reviews for a specific restaurant. Input should be a JSON string with fields: place_id, limit.",
            mcp_server_url=self.mcp_server_url,
            mcp_tool_name="get_reviews",
            api_key=self.mcp_api_key,
            input_schema={
                "type": "object",
                "properties": {
                    "place_id": {"type": "string"},
                    "limit": {"type": "integer"}
                }
            }
        )
        
        return [
            Tool(
                name="search_restaurants",
                description=search_tool.description,
                args_schema=search_tool.input_schema,
                coroutine=search_tool.ainvoke
            ),
            Tool(
                name="get_restaurant_details",
                description=details_tool.description,
                args_schema=details_tool.input_schema,
                coroutine=details_tool.ainvoke
            ),
            Tool(
                name="get_restaurant_reviews",
                description=reviews_tool.description,
                args_schema=reviews_tool.input_schema,
                coroutine=reviews_tool.ainvoke
            )
        ]
    
    def _create_mock_tools(self) -> List[Tool]:
        """Create mock tools for testing."""
        
        search_tool = MockMCPToolWrapper(
            name="search_restaurants",
            description="Search for restaurants by query, location, cuisine"
        )
        
        details_tool = MockMCPToolWrapper(
            name="get_restaurant_details",
            description="Get restaurant details by place ID"
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
