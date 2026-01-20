
import asyncio
import os
import sys
import json
from src.utils.mcp_client import call_mcp_tool

async def verify_tool(mcp_url: str, tool_name: str, **kwargs):
    print(f"\n--- 🛠️  Testing {tool_name} ---")
    print(f"    URL: {mcp_url}")
    try:
        result = await call_mcp_tool(mcp_url, tool_name, **kwargs)
        
        # Check for error dict
        if isinstance(result, dict) and "error" in result:
             print(f"    ❌ Tool Error: {result['error']}")
             return
            
        # Basic validation
        if result:
            s_res = str(result)
            preview = s_res[:100] + "..." if len(s_res) > 100 else s_res
            print(f"    ✅ Success! Result: {preview}")
            
            # Specific validation checks
            if tool_name == "get_financials" and "income_statement" in result:
                 print("       (Validated Financials Structure)")
            elif tool_name == "get_economic_data" and "history" in result:
                 print("       (Validated FRED Data Structure)")
            elif tool_name == "forecast_price" and "forecast" in result:
                 print("       (Validated Forecast Structure)")
                 
        else:
            print(f"    ⚠️  Empty Result.")
            
    except Exception as e:
        print(f"    ❌ Exception: {e}")

async def verify_all():
    print("🚀 Verifying ALL MCP Microservices...\n")
    
    # 1. Yahoo Finance
    yahoo_url = os.getenv("YAHOO_MCP_URL")
    if yahoo_url:
        await verify_tool(yahoo_url, "get_stock_info", ticker="NVDA")
        await verify_tool(yahoo_url, "get_financials", ticker="NVDA")
    else:
        print("⚠️  YAHOO_MCP_URL missing")

    # 2. FRED Economics
    fred_url = os.getenv("FRED_MCP_URL")
    if fred_url:
        # GDP is a safe test series
        await verify_tool(fred_url, "get_economic_data", series_id="GDP")
    else:
        print("⚠️  FRED_MCP_URL missing")

    # 3. Sentiment (News)
    sent_url = os.getenv("SENTIMENT_MCP_URL")
    if sent_url:
        await verify_tool(sent_url, "get_news_sentiment", ticker="AAPL", days=3)
        await verify_tool(sent_url, "get_reddit_sentiment", ticker="AAPL")
    else:
        print("⚠️  SENTIMENT_MCP_URL missing")

    # 4. Forecast
    forecast_url = os.getenv("FORECAST_MCP_URL")
    if forecast_url:
        await verify_tool(forecast_url, "forecast_price", ticker="MSFT", periods=7)
    else:
        print("⚠️  FORECAST_MCP_URL missing")

    print("\n🏁 Verification Complete.")

if __name__ == "__main__":
    asyncio.run(verify_all())
