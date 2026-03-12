"""MCP tool wrapper for LangChain tools."""

import json
from typing import Any, AsyncIterator, Optional

import aiohttp


class MCPToolWrapper:
    """
    Wrapper for MCP (Model Context Protocol) tools.
    
    This wraps MCP server tools to work with LangChain agents.
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        mcp_server_url: str,
        mcp_tool_name: str,
        api_key: Optional[str] = None,
        input_schema: Optional[dict] = None
    ):
        self.name = name
        self.description = description
        self.mcp_server_url = mcp_server_url
        self.mcp_tool_name = mcp_tool_name
        self.api_key = api_key
        self.input_schema = input_schema or {}
    
    async def ainvoke(self, input_str: str) -> str:
        """
        Execute the MCP tool.
        
        Args:
            input_str: JSON string with tool arguments
            
        Returns:
            Formatted string result
        """
        # Parse input
        try:
            params = json.loads(input_str) if input_str else {}
        except json.JSONDecodeError:
            # If not JSON, treat as query
            params = {"query": input_str}
        
        # Call MCP server
        results = []
        async for chunk in self._call_mcp(params):
            results.append(chunk)
        
        return self._format_results(results)
    
    async def _call_mcp(self, params: dict) -> AsyncIterator[dict]:
        """Call the MCP server."""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        timeout = aiohttp.ClientTimeout(total=30)
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            try:
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
                    if response.status != 200:
                        yield {"error": f"HTTP {response.status}: {await response.text()}"}
                        return
                    
                    async for line in response.content:
                        if line:
                            try:
                                data = json.loads(line)
                                if "result" in data:
                                    result = data["result"]
                                    # Handle both single results and arrays
                                    if isinstance(result, list):
                                        for item in result:
                                            yield item
                                    else:
                                        yield result
                                elif "error" in data:
                                    yield {"error": data["error"]}
                            except json.JSONDecodeError:
                                continue
                            
            except aiohttp.ClientError as e:
                yield {"error": str(e)}
    
    def _format_results(self, results: list) -> str:
        """Format tool results for the agent."""
        if not results:
            return "No results found."
        
        # Filter out errors
        valid_results = [r for r in results if "error" not in r]
        
        if not valid_results:
            error_messages = [r.get("error", "Unknown error") for r in results]
            return f"Error: {', '.join(error_messages)}"
        
        # Format as readable text
        formatted = []
        for r in valid_results:
            if isinstance(r, dict):
                # Restaurant result
                name = r.get("name", r.get("displayName", "Restaurant"))
                rating = r.get("rating", "N/A")
                price = r.get("price_level", r.get("priceLevel", ""))
                address = r.get("vicinity", r.get("formatted_address", ""))
                
                price_str = "$" * price if isinstance(price, int) else ""
                
                formatted.append(
                    f"• {name}\n"
                    f"  Rating: {rating}{' ' + price_str if price_str else ''}\n"
                    f"  Address: {address}"
                )
        
        if formatted:
            return "\n\n".join(formatted)
        
        return str(valid_results)


class MockMCPToolWrapper:
    """
    Mock tool for testing without MCP server.
    """
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    async def ainvoke(self, input_str: str) -> str:
        """Return mock data."""
        # Return sample restaurant data
        return """• The Italian Garden
  Rating: 4.5 $$ 
  Address: 123 Main Street, San Francisco, CA

• Luigi's Trattoria
  Rating: 4.3 $$ 
  Address: 456 Oak Avenue, San Francisco, CA

• Bella Italia
  Rating: 4.7 $$$ 
  Address: 789 Pine Street, San Francisco, CA"""
