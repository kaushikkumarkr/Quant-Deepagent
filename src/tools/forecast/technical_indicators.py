import pandas as pd
import numpy as np
from typing import Dict, Any
from src.tools.financial.yahoo_finance import YahooFinanceTool
from src.utils.cache import disk_cache
from src.utils.logging import setup_logging

logger = setup_logging(__name__)

class TechnicalAnalysis:
    """
    Tool for calculating standard technical indicators.
    """
    
    def __init__(self):
        self.yf_tool = YahooFinanceTool()

    @disk_cache(expire=3600)
    def calculate_indicators(self, ticker: str) -> Dict[str, Any]:
        """
        Calculate SMA, RSI, MACD, Bollinger Bands, Volatility.
        """
        # Get 1 year of data for sufficient lookback (200 SMA)
        hist = self.yf_tool.get_price_history(ticker, period="1y")
        if not hist or "error" in hist:
            return {"error": "Data unavailable"}
            
        try:
            df = pd.DataFrame(hist)
            df['Close'] = pd.to_numeric(df['Close'])
            close = df['Close']
            
            # 1. Simple Moving Averages (SMA)
            sma_20 = close.rolling(window=20).mean().iloc[-1]
            sma_50 = close.rolling(window=50).mean().iloc[-1]
            sma_200 = close.rolling(window=200).mean().iloc[-1]
            
            # 2. RSI (14)
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs)).iloc[-1]
            
            # 3. MACD (12, 26, 9)
            exp1 = close.ewm(span=12, adjust=False).mean()
            exp2 = close.ewm(span=26, adjust=False).mean()
            macd = exp1 - exp2
            signal = macd.ewm(span=9, adjust=False).mean()
            
            macd_val = macd.iloc[-1]
            signal_val = signal.iloc[-1]
            
            # 4. Bollinger Bands (20, 2)
            rolling_mean = close.rolling(window=20).mean()
            rolling_std = close.rolling(window=20).std()
            upper_band = rolling_mean + (rolling_std * 2)
            lower_band = rolling_mean - (rolling_std * 2)
            
            bb_upper = upper_band.iloc[-1]
            bb_lower = lower_band.iloc[-1]
            
            # 5. Volatility (Annualized)
            # Log returns
            log_returns = np.log(close / close.shift(1))
            hist_volatility = log_returns.std() * np.sqrt(252) * 100 # Annualized %
            
            # Interpretations
            current_price = close.iloc[-1]
            signals = []
            
            if rsi > 70: signals.append("Overbought (RSI > 70)")
            elif rsi < 30: signals.append("Oversold (RSI < 30)")
            
            if current_price > sma_200: signals.append("Bullish Trend (> 200 SMA)")
            else: signals.append("Bearish Trend (< 200 SMA)")
            
            if macd_val > signal_val: signals.append("MACD Bullish Crossover")
            
            return {
                "ticker": ticker,
                "current_price": float(current_price),
                "sma_20": float(sma_20),
                "sma_50": float(sma_50),
                "sma_200": float(sma_200),
                "rsi_14": float(rsi),
                "macd": float(macd_val),
                "macd_signal": float(signal_val),
                "bb_upper": float(bb_upper),
                "bb_lower": float(bb_lower),
                "volatility_annualized_pct": float(hist_volatility),
                "signals": signals
            }
            
        except Exception as e:
            logger.error(f"Technical analysis failed for {ticker}: {e}")
            return {"error": str(e)}
