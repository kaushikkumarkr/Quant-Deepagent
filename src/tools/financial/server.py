
from fastmcp import FastMCP
from src.tools.financial.yahoo_finance import YahooFinanceTool

# Create FastMCP server
mcp = FastMCP("yahoo-finance")

# Register tools
@mcp.tool()
def get_stock_info(ticker: str) -> dict:
    """Get basic stock information (price, market cap, P/E, etc.)"""
    return YahooFinanceTool.get_stock_info(ticker)

@mcp.tool()
def get_financials(ticker: str) -> dict:
    """Get annual financials: Income Statement, Balance Sheet, Cash Flow."""
    return YahooFinanceTool.get_financials(ticker)

@mcp.tool()
def get_earnings(ticker: str) -> dict:
    """Get earnings history and upcoming dates."""
    return YahooFinanceTool.get_earnings(ticker)

@mcp.tool()
def get_recommendations(ticker: str) -> dict:
    """Get analyst recommendations."""
    return {"recommendations": YahooFinanceTool.get_recommendations(ticker)}

@mcp.tool()
def get_price_history(ticker: str, period: str = "2y") -> dict:
    """Get historical price data (ohlcv) for forecasting."""
    return {"history": YahooFinanceTool.get_price_history(ticker, period)}

if __name__ == "__main__":
    mcp.run()
