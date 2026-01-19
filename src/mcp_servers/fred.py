from fastmcp import FastMCP
from fredapi import Fred
from typing import Dict, Any, List
import os
import sys
import warnings

# Suppress warnings
warnings.filterwarnings("ignore")

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.config import settings

# Initialize FastMCP Server
mcp = FastMCP("fred-economics")

# Helper to get client
def get_fred_client():
    api_key = settings.fred_api_key or os.getenv("FRED_API_KEY")
    if not api_key:
        raise ValueError("FRED API Key not found. Please set FRED_API_KEY environment variable.")
    return Fred(api_key=api_key)

@mcp.tool()
def get_economic_data(series_id: str = "GDP") -> str:
    """
    Get latest observations for an economic series from FRED.
    Common IDs: GDP, CPIAUCSL (CPI), UNRATE (Unemployment), DGS10 (10Y Treasury), VIXCLS (VIX).
    """
    try:
        fred = get_fred_client()
        
        # Sanitize input
        if series_id.upper().startswith("FRED/"):
            series_id = series_id[5:]
        
        # Fetch last 12 observations
        data = fred.get_series(series_id)
        
        if data is None or data.empty:
            return f"No data found for {series_id}"
            
        # Get latest value and trend (last 12 points)
        latest_date = data.index[-1].strftime('%Y-%m-%d')
        latest_value = float(data.iloc[-1])
        
        recent_history = [
            {"date": d.strftime('%Y-%m-%d'), "value": float(v)}
            for d, v in data.tail(12).items() 
        ]
        
        result = {
            "series_id": series_id,
            "latest_date": latest_date,
            "latest_value": latest_value,
            "history": recent_history,
            "units": fred.get_series_info(series_id).get('units')
        }
        return str(result)
        
    except Exception as e:
        return f"Error fetching FRED series {series_id}: {e}"

if __name__ == "__main__":
    mcp.run()
