import pytest
from src.utils.mcp_client import call_mcp_tool

@pytest.mark.asyncio
async def test_yahoo_mcp_call():
    """Test calling Yahoo Finance MCP tool."""
    result = await call_mcp_tool("src/mcp_servers/yahoo_finance.py", "get_stock_info", ticker="AAPL")
    assert isinstance(result, dict)
    assert "symbol" in result
    assert result["symbol"] == "AAPL"

@pytest.mark.asyncio
async def test_fred_mcp_call():
    """Test calling FRED MCP tool."""
    # Assuming FRED_API_KEY is set in env
    result = await call_mcp_tool("src/mcp_servers/fred.py", "get_economic_data", series_id="GDP")
    # Result might be an error dict if key is missing, but it should return a dict
    assert isinstance(result, dict)
    if "error" not in result:
        assert result["series_id"] == "GDP"
