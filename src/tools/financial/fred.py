from typing import Dict, Any, Optional
from fredapi import Fred
from src.config import settings
from src.utils.cache import disk_cache
from src.utils.retry import with_retry
from src.utils.logging import setup_logging

logger = setup_logging(__name__)

class FREDTool:
    """
    Tool for fetching macroeconomic data from Federal Reserve Economic Data (FRED).
    """

    def __init__(self):
        self.api_key = settings.fred_api_key
        self.client = None
        if self.api_key:
            self.client = Fred(api_key=self.api_key)
        else:
            logger.warning("FRED API Key not found. Macro data will be unavailable.")

    @disk_cache(expire=86400) # Cache for 24 hours (macro data changes slowly)
    @with_retry(max_attempts=3)
    def get_economic_data(self, series_id: str = "GDP") -> Dict[str, Any]:
        """
        Get latest observations for an economic series.
        Common IDs: GDP, CPIAUCSL (CPI), UNRATE (Unemployment), DGS10 (10Y Treasury), VIXCLS (VIX).
        """
        if not self.client:
            return {"error": "FRED API Key missing"}
        
        # Sanitize input: Remove common prefixes like "FRED/" that agents might add
        if series_id.upper().startswith("FRED/"):
            series_id = series_id[5:]
        
        # Validate against known good series IDs
        VALID_SERIES = ["GDP", "DGS10", "DGS2", "UNRATE", "CPIAUCSL", "VIXCLS", "FEDFUNDS", "M2SL", "UMCSENT"]
        if series_id.upper() not in VALID_SERIES:
            return {"error": f"Invalid series ID '{series_id}'. Valid options: {', '.join(VALID_SERIES)}"}

        try:
            # Fetch last 12 observations
            data = self.client.get_series(series_id)
            
            if data is None or data.empty:
                return {"error": f"No data found for {series_id}"}
                
            # Get latest value and trend (last 5 points)
            latest_date = data.index[-1].strftime('%Y-%m-%d')
            latest_value = float(data.iloc[-1])
            
            recent_history = [
                {"date": d.strftime('%Y-%m-%d'), "value": float(v)}
                for d, v in data.tail(12).items() 
            ]
            
            return {
                "series_id": series_id,
                "latest_date": latest_date,
                "latest_value": latest_value,
                "history": recent_history,
                "units": self.client.get_series_info(series_id).get('units')
            }
            
        except Exception as e:
            logger.error(f"Error fetching FRED series {series_id}: {e}")
            return {"error": str(e)}
