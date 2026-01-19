from fastmcp import FastMCP
import yfinance as yf
import pandas as pd
from typing import Dict, Any, List
import sys
import os
import warnings

# Suppress warnings
warnings.filterwarnings("ignore")

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))


# Initialize FastMCP Server
mcp = FastMCP("yahoo-finance")

@mcp.tool()
def get_stock_info(ticker: str) -> str:
    """
    Get basic stock information (price, market cap, P/E, etc.)
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Select key fields to reduce noise
        key_fields = [
            'symbol', 'shortName', 'longName', 'sector', 'industry',
            'marketCap', 'currentPrice', 'targetMeanPrice', 
            'trailingPE', 'forwardPE', 'dividendYield', 'beta',
            'fiftyTwoWeekHigh', 'fiftyTwoWeekLow', 'averageVolume',
            'website', 'longBusinessSummary'
        ]
        
        data = {k: info.get(k) for k in key_fields if k in info}
        return str(data)
    except Exception as e:
        return f"Error fetching info for {ticker}: {e}"

@mcp.tool()
def get_financials(ticker: str) -> str:
    """
    Get annual financials: Income Statement, Balance Sheet, Cash Flow.
    """
    try:
        stock = yf.Ticker(ticker)
        
        # Convert DataFrames to dictionaries (handling timestamps)
        def df_to_dict(df):
            if df.empty: return {}
            # Convert timestamp columns to strings
            df.columns = [d.strftime('%Y-%m-%d') if hasattr(d, 'strftime') else str(d) for d in df.columns]
            return df.to_dict()

        data = {
            "income_statement": df_to_dict(stock.financials),
            "balance_sheet": df_to_dict(stock.balance_sheet),
            "cash_flow": df_to_dict(stock.cashflow)
        }
        return str(data)
    except Exception as e:
        return f"Error fetching financials for {ticker}: {e}"

@mcp.tool()
def get_earnings(ticker: str) -> str:
    """
    Get earnings history.
    """
    try:
        stock = yf.Ticker(ticker)
        history = stock.earnings_history
        if history is None or history.empty:
            return "No earnings history available."
        return str(history.to_dict('records'))
    except Exception as e:
        return f"Error fetching earnings for {ticker}: {e}"

if __name__ == "__main__":
    mcp.run()
