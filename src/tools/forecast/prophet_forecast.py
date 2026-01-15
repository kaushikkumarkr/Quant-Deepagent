import pandas as pd
from prophet import Prophet
from typing import Dict, Any, List, Optional
from src.tools.financial.yahoo_finance import YahooFinanceTool
from src.utils.cache import disk_cache
from src.utils.logging import setup_logging
import logging

# Prophet is noisy
logging.getLogger('cmdstanpy').setLevel(logging.WARNING)
logging.getLogger('prophet').setLevel(logging.WARNING)

logger = setup_logging(__name__)

class ProphetTool:
    """
    Tool for price forecasting using Meta's Prophet model.
    """
    
    def __init__(self):
        self.yf_tool = YahooFinanceTool()

    @disk_cache(expire=3600*12) # Cache for 12 hours
    def forecast_price(self, ticker: str, periods: int = 30) -> Dict[str, Any]:
        """
        Generate a price forecast for the next N days.
        """
        logger.info(f"Generating Prophet forecast for {ticker}...")
        
        # 1. Get Historical Data (2 years)
        hist_data = self.yf_tool.get_price_history(ticker, period="2y")
        if not hist_data or "error" in hist_data:
            return {"error": "Insufficient data for forecasting"}
            
        try:
            # 2. Prepare Data for Prophet (ds, y)
            df = pd.DataFrame(hist_data)
            df['ds'] = pd.to_datetime(df['Date'])
            df['y'] = df['Close']
            df = df[['ds', 'y']]
            
            # 3. Fit Model
            # Daily data, disable intraday
            m = Prophet(daily_seasonality=True, yearly_seasonality=True, weekly_seasonality=True)
            m.fit(df)
            
            # 4. Predict
            future = m.make_future_dataframe(periods=periods)
            forecast = m.predict(future)
            
            # 5. Extract Results
            # Last 'periods' rows are the prediction
            prediction = forecast.tail(periods)
            
            current_price = df.iloc[-1]['y']
            target_price = prediction.iloc[-1]['yhat']
            upper_bound = prediction.iloc[-1]['yhat_upper']
            lower_bound = prediction.iloc[-1]['yhat_lower']
            
            change_pct = ((target_price - current_price) / current_price) * 100
            
            # Trend direction
            trend = "neutral"
            if change_pct > 2: trend = "bullish"
            elif change_pct < -2: trend = "bearish"
            
            return {
                "ticker": ticker,
                "current_price": float(current_price),
                "forecast_price_30d": float(target_price),
                "forecast_upper": float(upper_bound),
                "forecast_lower": float(lower_bound),
                "change_pct": float(change_pct),
                "trend": trend,
                "confidence_interval": [float(lower_bound), float(upper_bound)],
                "forecast_data": prediction[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(periods).to_dict('records') # Convert timestamps to str?
            }
            
        except Exception as e:
            logger.error(f"Prophet forecast failed for {ticker}: {e}")
            return {"error": str(e)}
