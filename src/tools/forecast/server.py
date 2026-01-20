
from fastmcp import FastMCP
from src.tools.forecast.prophet_forecast import ProphetTool
from src.tools.forecast.technical_indicators import TechnicalAnalysis

# Create FastMCP server
mcp = FastMCP("forecast-analytics")

@mcp.tool()
def forecast_price(ticker: str, periods: int = 30) -> dict:
    """
    Generate a price forecast for the next N days using Prophet.
    """
    tool = ProphetTool()
    return {"forecast": tool.forecast_price(ticker, periods=periods)}

@mcp.tool()
def get_technical_indicators(ticker: str) -> dict:
    """
    Calculate SMA, RSI, MACD, Bollinger Bands, Volatility.
    """
    tool = TechnicalAnalysis()
    return {"indicators": tool.calculate_indicators(ticker)}

if __name__ == "__main__":
    mcp.run()
