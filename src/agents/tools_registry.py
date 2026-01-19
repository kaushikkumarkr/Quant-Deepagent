import os
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from src.utils.mcp_client import call_mcp_tool

# --- Input Schemas ---

class TickerInput(BaseModel):
    ticker: str = Field(description="Stock ticker symbol (e.g., AAPL, NVDA)")

class SeriesInput(BaseModel):
    series_id: str = Field(description="FRED Economic Series ID (e.g., GDP, UNRATE)")

class ForecastInput(BaseModel):
    ticker: str = Field(description="Stock ticker symbol")
    periods: int = Field(default=30, description="Number of days to forecast")

# --- Async Implementations ---

# Yahoo Finance
async def get_stock_info(ticker: str) -> str:
    return await call_mcp_tool("src/mcp_servers/yahoo_finance.py", "get_stock_info", ticker=ticker)

async def get_financials(ticker: str) -> str:
    return await call_mcp_tool("src/mcp_servers/yahoo_finance.py", "get_financials", ticker=ticker)

async def get_earnings(ticker: str) -> str:
    return await call_mcp_tool("src/mcp_servers/yahoo_finance.py", "get_earnings", ticker=ticker)

# FRED
async def get_economic_data(series_id: str) -> str:
    return await call_mcp_tool("src/mcp_servers/fred.py", "get_economic_data", series_id=series_id)

# Sentiment
async def get_news_sentiment(ticker: str) -> str:
    return await call_mcp_tool("src/mcp_servers/sentiment.py", "get_news_sentiment", ticker=ticker)

# Forecast
async def forecast_price(ticker: str, periods: int = 30) -> str:
    return await call_mcp_tool("src/mcp_servers/forecast.py", "forecast_price", ticker=ticker, periods=periods)

# --- Tool Definitions ---

yahoo_info_tool = StructuredTool.from_function(
    coroutine=get_stock_info,
    func=None, # Async only
    name="get_stock_info",
    description="Get basic stock information (price, market cap, P/E, etc.)",
    args_schema=TickerInput
)

yahoo_financials_tool = StructuredTool.from_function(
    coroutine=get_financials,
    func=None,
    name="get_financials",
    description="Get annual financials: Income Statement, Balance Sheet, Cash Flow.",
    args_schema=TickerInput
)

yahoo_earnings_tool = StructuredTool.from_function(
    coroutine=get_earnings,
    func=None,
    name="get_earnings",
    description="Get earnings history.",
    args_schema=TickerInput
)

fred_tool = StructuredTool.from_function(
    coroutine=get_economic_data,
    func=None,
    name="get_economic_data",
    description="Get economic data from FRED (GDP, UNRATE, CPIAUCSL, etc.)",
    args_schema=SeriesInput
)

sentiment_tool = StructuredTool.from_function(
    coroutine=get_news_sentiment,
    func=None,
    name="get_news_sentiment",
    description="Get market sentiment and news for a ticker.",
    args_schema=TickerInput
)

forecast_tool = StructuredTool.from_function(
    coroutine=forecast_price,
    func=None,
    name="forecast_price",
    description="Forecast stock prices using Prophet model.",
    args_schema=ForecastInput
)

# --- EXPORT LISTS ---

FUNDAMENTALS_TOOLS = [yahoo_info_tool, yahoo_financials_tool, yahoo_earnings_tool, fred_tool]
SENTIMENT_TOOLS = [sentiment_tool]
FORECAST_TOOLS = [forecast_tool]
