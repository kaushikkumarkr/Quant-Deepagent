from langchain_core.tools import tool
from src.tools.financial.yahoo_finance import YahooFinanceTool
from src.tools.financial.fred import FREDTool
from src.tools.financial.sec_edgar import SECTool
from src.tools.sentiment.news_api import NewsAPITool
from src.tools.forecast.prophet_forecast import ProphetTool
from src.tools.forecast.technical_indicators import TechnicalAnalysis

# Initialize instances
yf_tool = YahooFinanceTool()
fred_tool = FREDTool()
sec_tool = SECTool()
news_tool = NewsAPITool()
prophet_tool = ProphetTool()
tech_tool = TechnicalAnalysis()

# --- Fundamentals Tools ---
@tool
def get_stock_info(ticker: str):
    """Get company profile (sector, market cap, etc)."""
    return yf_tool.get_stock_info(ticker)

@tool
def get_financials(ticker: str):
    """Get financial statements (income, balance sheet, cash flow)."""
    return yf_tool.get_financials(ticker)

@tool
def get_macro_data(series_id: str):
    """Get macroeconomic data from FRED (e.g., GDP, UNRATE)."""
    return fred_tool.get_economic_data(series_id)

@tool
def get_filiings(ticker: str):
    """Get SEC filings text."""
    files = sec_tool.download_filings(ticker, limit=1)
    if not files: return "No filings found."
    return sec_tool.extract_text(files[0])[:5000]

# --- Sentiment Tools ---
@tool
def analyze_news_sentiment(ticker: str):
    """Search news and return raw articles for analysis."""
    # NewsAPI returns articles, analysis happens in agent or we can add a wrapper.
    # For now, return raw news.
    return news_tool.get_news(ticker)

# --- Forecast Tools ---
@tool
def forecast_price(ticker: str):
    """Forecast future price using Prophet."""
    return prophet_tool.forecast_price(ticker)

@tool
def get_technical_indicators(ticker: str):
    """Get technical analysis indicators (RSI, MACD, etc)."""
    return tech_tool.calculate_indicators(ticker)

# Tool Sets for Agents
fundamentals_tools = [get_stock_info, get_financials, get_macro_data, get_filiings]
sentiment_tools = [analyze_news_sentiment] # Removed reddit
forecast_tools = [forecast_price, get_technical_indicators]

