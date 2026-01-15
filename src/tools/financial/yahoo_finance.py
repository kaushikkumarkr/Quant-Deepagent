import yfinance as yf
import pandas as pd
from typing import Dict, Any, Optional
from src.utils.cache import disk_cache
from src.utils.retry import with_retry
from src.utils.logging import setup_logging

logger = setup_logging(__name__)

class YahooFinanceTool:
    """
    Tool for fetching financial data using yfinance.
    """
    
    @staticmethod
    @disk_cache(expire=3600)  # Cache for 1 hour
    @with_retry(max_attempts=3)
    def get_stock_info(ticker: str) -> Dict[str, Any]:
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
            
            return {k: info.get(k) for k in key_fields if k in info}
        except Exception as e:
            logger.error(f"Error fetching info for {ticker}: {e}")
            return {"error": str(e)}

    @staticmethod
    @disk_cache(expire=86400)  # Cache for 24 hours
    @with_retry(max_attempts=3)
    def get_financials(ticker: str) -> Dict[str, Any]:
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

            return {
                "income_statement": df_to_dict(stock.financials),
                "balance_sheet": df_to_dict(stock.balance_sheet),
                "cash_flow": df_to_dict(stock.cashflow)
            }
        except Exception as e:
            logger.error(f"Error fetching financials for {ticker}: {e}")
            return {"error": str(e)}

    @staticmethod
    @disk_cache(expire=86400)
    @with_retry(max_attempts=3)
    def get_earnings(ticker: str) -> Dict[str, Any]:
        """
        Get earnings history and upcoming dates.
        """
        try:
            stock = yf.Ticker(ticker)
            calendar = stock.calendar
            
            # Helper to safely serialize calendar
            cal_dict = {}
            if isinstance(calendar, dict):
                cal_dict = calendar
            elif hasattr(calendar, 'to_dict'): # older yfinance versions
                cal_dict = calendar.to_dict()

            return {
                "calendar": cal_dict,
                "earnings_history": stock.earnings_history.to_dict('records') if not stock.earnings_history.empty else []
            }
        except Exception as e:
            # Calendar often fails on yfinance, fail gracefully
            logger.warning(f"Error fetching earnings for {ticker}: {e}")
            return {"error": "Data unavailable"}
            
    @staticmethod
    @disk_cache(expire=86400)
    def get_recommendations(ticker: str) -> list[Dict[str, Any]]:
        """
        Get analyst recommendations.
        """
        try:
            stock = yf.Ticker(ticker)
            recs = stock.recommendations
            if recs is None or recs.empty:
                return []
            
            # Format to list of dicts
            return recs.tail(10).reset_index().to_dict('records')
        except Exception as e:
            logger.error(f"Error fetching recommendations for {ticker}: {e}")
            return []

    @staticmethod
    @disk_cache(expire=1800) # 30 mins
    def get_price_history(ticker: str, period="2y") -> Dict[str, Any]:
        """
        Get historical price data (ohlcv) for forecasting.
        """
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)
            if hist.empty:
                return {}
            
            # Reset index to get Date as a column and convert to string
            hist = hist.reset_index()
            hist['Date'] = hist['Date'].dt.strftime('%Y-%m-%d')
            
            return hist.to_dict('records')
        except Exception as e:
            logger.error(f"Error fetching price history for {ticker}: {e}")
            return {"error": str(e)}
