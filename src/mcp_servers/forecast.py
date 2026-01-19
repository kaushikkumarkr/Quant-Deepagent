from fastmcp import FastMCP
import sys
import os
import warnings
import pandas as pd
import numpy as np

# Suppress warnings
warnings.filterwarnings("ignore")

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.tools.forecast.prophet_forecast import ProphetTool
from src.tools.forecast.technical_indicators import TechnicalAnalysis
from src.utils.logging import setup_logging

logger = setup_logging(__name__)

# Initialize FastMCP Server
mcp = FastMCP("forecast-analytics")

@mcp.tool()
def forecast_price(ticker: str, periods: int = 30) -> str:
    """
    Generate a price forecast for the next N days using Prophet.
    """
    try:
        tool = ProphetTool()
        result = tool.forecast_price(ticker, periods=periods)
        return str(result)
    except Exception as e:
        return f"Error forecasting for {ticker}: {e}"

@mcp.tool()
def get_technical_indicators(ticker: str) -> str:
    """
    Calculate SMA, RSI, MACD, Bollinger Bands, Volatility.
    """
    try:
        tool = TechnicalAnalysis()
        result = tool.calculate_indicators(ticker)
        return str(result)
    except Exception as e:
        return f"Error calculating indicators for {ticker}: {e}"

if __name__ == "__main__":
    mcp.run()
