import json
from fastmcp import Client
from src.utils.logging import setup_logging
from typing import Any

logger = setup_logging(__name__)

async def call_mcp_tool(server_path: str, tool_name: str, **kwargs) -> Any:
    """
    Helper to call a FastMCP server tool via Client (Stdio) or SSE.
    """
    try:
        if server_path.startswith("http"):
            # SSE Mode (Docker/Remote)
            from mcp.client.sse import sse_client
            from mcp.client.session import ClientSession
            
            async with sse_client(url=server_path) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    result = await session.call_tool(tool_name, arguments=kwargs)
                    output = result.content[0].text
        else:
            # Stdio Mode (Local Script)
            # Use Client context manager to connect to the server script
            async with Client(server_path) as client:
                result = await client.call_tool(tool_name, kwargs)
                output = result.content[0].text
        
        # Attempt to parse specific stringified outputs
        try:
            # First try JSON parsing (standard for MCP)
            return json.loads(output)
        except:
            try:
                # Fallback to literal_eval (for Python dict reprs)
                import ast
                val = ast.literal_eval(output)
                return val
            except:
                # Return raw text if parsing fails
                return output
            
    except Exception as e:
        logger.error(f"MCP Call Error: {e}")
        return {"error": str(e)}
