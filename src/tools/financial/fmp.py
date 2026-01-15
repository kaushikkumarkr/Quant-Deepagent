import requests
from typing import Dict, Any, List, Optional
from src.config import settings
from src.utils.cache import disk_cache
from src.utils.retry import with_retry
from src.utils.logging import setup_logging

logger = setup_logging(__name__)

class FMPTool:
    """
    Tool for fetching financial data from Financial Modeling Prep.
    """
    
    BASE_URL = "https://financialmodelingprep.com/api/v3"

    def __init__(self):
        self.api_key = settings.fmp_api_key
        if not self.api_key:
            logger.warning("FMP API Key not found. Financial data will be limited.")

    def _get(self, endpoint: str, params: Dict = None) -> Any:
        if not self.api_key:
            return {"error": "API Key missing"}
            
        params = params or {}
        params['apikey'] = self.api_key
        
        url = f"{self.BASE_URL}/{endpoint}"
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            if isinstance(data, list) and len(data) == 0:
                return {} # Empty list means no data found usually
            return data
        except Exception as e:
            logger.error(f"FMP Request failed ({endpoint}): {e}")
            return {"error": str(e)}

    @disk_cache(expire=86400)
    @with_retry(max_attempts=3)
    def get_profile(self, ticker: str) -> Dict[str, Any]:
        """Get company profile (sector, description, mkt cap)."""
        data = self._get(f"profile/{ticker}")
        if isinstance(data, list) and len(data) > 0:
            return data[0]
        return data

    @disk_cache(expire=86400)
    @with_retry(max_attempts=3)
    def get_financials(self, ticker: str, limit: int = 1) -> Dict[str, Any]:
        """Get combined financial statements."""
        income = self._get(f"income-statement/{ticker}", {"limit": limit})
        balance = self._get(f"balance-sheet-statement/{ticker}", {"limit": limit})
        cash = self._get(f"cash-flow-statement/{ticker}", {"limit": limit})
        
        return {
            "income_statement": income if not isinstance(income, dict) else [],
            "balance_sheet": balance if not isinstance(balance, dict) else [],
            "cash_flow": cash if not isinstance(cash, dict) else []
        }

    @disk_cache(expire=86400)
    def get_growth_metrics(self, ticker: str) -> Dict[str, Any]:
        """Get financial growth metrics."""
        data = self._get(f"financial-growth/{ticker}", {"limit": 1})
        if isinstance(data, list) and len(data) > 0:
            return data[0]
        return {}
