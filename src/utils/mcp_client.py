import json
from fastmcp import Client
from src.utils.logging import setup_logging
from typing import Any

logger = setup_logging(__name__)

async def call_mcp_tool(server_path: str, tool_name: str, **kwargs) -> Any:
    """
    Helper to call a FastMCP server tool via Client.
    """
    try:
        # Use Client context manager to connect to the server script
        async with Client(server_path) as client:
            result = await client.call_tool(tool_name, kwargs)
            
            # FastMCP result.content is a list of TextContent/ImageContent
            # We assume simple text output for our tools
            output = result.content[0].text
            
            # Attempt to parse specific stringified outputs
            try:
                # Our tools return str(dict), so we can try to parse it
                import ast
                return ast.literal_eval(output)
            except:
                return output
                
    except Exception as e:
        logger.error(f"MCP Call Error: {e}")
        return {"error": str(e)}
