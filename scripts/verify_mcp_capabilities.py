
import asyncio
import os
import sys
from src.utils.mcp_client import call_mcp_tool

async def check_mcp_yahoo():
    """
    Exhaustively verify all capabilities of the Dockerized Yahoo Finance MCP Server.
    """
    yahoo_url = os.getenv("YAHOO_MCP_URL")
    if not yahoo_url:
        print("❌ YAHOO_MCP_URL is not set.")
        sys.exit(1)
        
    print(f"🚀 Verifying MCP Capabilities at: {yahoo_url}\n")
    
    TICKERS = ["MSFT", "GOOGL"]
    
    for ticker in TICKERS:
        print(f"--- 🔍 Analyzing {ticker} ---")
        
        # 1. Financials
        try:
            print(f"   [1/3] Fetching Financials...")
            fin = await call_mcp_tool(yahoo_url, "get_financials", ticker=ticker)
            if isinstance(fin, dict) and "income_statement" in fin:
                print(f"      ✅ Success. Keys: {list(fin.keys())}")
            else:
                print(f"      ❌ Failed: {str(fin)[:100]}")
        except Exception as e:
            print(f"      ❌ Exception: {e}")

        # 2. Earnings
        try:
            print(f"   [2/3] Fetching Earnings...")
            earn = await call_mcp_tool(yahoo_url, "get_earnings", ticker=ticker)
            if isinstance(earn, dict) and "earnings_history" in earn:
                history_count = len(earn['earnings_history'])
                print(f"      ✅ Success. Found {history_count} history records.")
            else:
                print(f"      ⚠️  Partial/No Data: {str(earn)[:100]}")
        except Exception as e:
            print(f"      ❌ Exception: {e}")
            
        # 3. Price History (for charts)
        try:
            print(f"   [3/3] Fetching Price History (2y)...")
            hist_resp = await call_mcp_tool(yahoo_url, "get_price_history", ticker=ticker, period="1mo")
            if isinstance(hist_resp, dict) and "history" in hist_resp:
                hist = hist_resp["history"]
                if isinstance(hist, list) and len(hist) > 0:
                    print(f"      ✅ Success. Retrieved {len(hist)} candle records.")
                    print(f"      Example: {hist[0]}")
                else:
                    print(f"      ❌ Failed: Empty history list.")
            else:
                print(f"      ❌ Failed: {str(hist_resp)[:100]}")
        except Exception as e:
            print(f"      ❌ Exception: {e}")
            
        print("")

    print("🏁 Complete.")

if __name__ == "__main__":
    asyncio.run(check_mcp_yahoo())
