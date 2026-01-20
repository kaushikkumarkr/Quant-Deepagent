
from fredapi import Fred
from typing import Dict, Any
import os
from src.utils.cache import disk_cache
from src.utils.retry import with_retry
from src.utils.logging import setup_logging

logger = setup_logging(__name__)

class FredTool:
    """
    Tool for fetching economic data using FRED API.
    """

    @staticmethod
    def get_client():
        api_key = os.getenv("FRED_API_KEY")
        if not api_key:
            raise ValueError("FRED_API_KEY not found in environment")
        return Fred(api_key=api_key)

    @staticmethod
    @disk_cache(expire=86400) # 24h cache for economic data
    @with_retry(max_attempts=3)
    def get_economic_data(series_id: str = "GDP") -> Dict[str, Any]:
        """
        Get latest observations for an economic series from FRED.
        """
        try:
            # Sanitize input
            if series_id.upper().startswith("FRED/"):
                series_id = series_id[5:]
            
            fred = FredTool.get_client()
            
            # Fetch last 12 observations
            data = fred.get_series(series_id)
            
            if data is None or data.empty:
                return {"error": f"No data found for {series_id}"}
                
            # Get latest value and trend (last 12 points)
            latest_date = data.index[-1].strftime('%Y-%m-%d')
            latest_value = float(data.iloc[-1])
            
            recent_history = [
                {"date": d.strftime('%Y-%m-%d'), "value": float(v)}
                for d, v in data.tail(12).items() 
            ]
            
            # Try to get metadata (units)
            try:
                info = fred.get_series_info(series_id)
                units = info.get('units') if info is not None else "Unknown"
            except:
                units = "Unknown"
            
            return {
                "series_id": series_id,
                "latest_date": latest_date,
                "latest_value": latest_value,
                "history": recent_history,
                "units": units
            }
            
        except Exception as e:
            logger.error(f"Error fetching FRED series {series_id}: {e}")
            return {"error": str(e)}
