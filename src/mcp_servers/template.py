from fastmcp import FastMCP

# Initialize FastMCP Server
# Usage: fastmcp run src/mcp_servers/template.py
mcp = FastMCP("generic-server")

@mcp.tool()
def example_tool(text: str) -> str:
    """
    Example tool description.
    """
    return f"Processed: {text}"

if __name__ == "__main__":
    mcp.run()
