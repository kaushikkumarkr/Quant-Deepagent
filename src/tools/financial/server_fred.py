
from fastmcp import FastMCP
from src.tools.financial.fred import FredTool

# Create FastMCP server
mcp = FastMCP("fred-economics")

@mcp.tool()
def get_economic_data(series_id: str = "GDP") -> dict:
    """
    Get latest observations for an economic series from FRED.
    Common IDs: GDP, CPIAUCSL (CPI), UNRATE (Unemployment), DGS10 (10Y Treasury), VIXCLS (VIX).
    """
    return FredTool.get_economic_data(series_id)

if __name__ == "__main__":
    mcp.run()
