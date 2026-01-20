
import asyncio
import os
import sys
from src.utils.mcp_client import call_mcp_tool

async def verify_mcp_standalone():
    print(f"🚀 Verifying Dockerized MCP Server (Yahoo Finance)...")
    
    # Check Env Var
    yahoo_url = os.getenv("YAHOO_MCP_URL")
    if not yahoo_url:
        print("❌ YAHOO_MCP_URL is not set.")
        sys.exit(1)
        
    print(f"📡 Connecting to: {yahoo_url}")
    
    try:
        # Test 1: Stock Info
        print("   Fetching AAPL info...")
        result = await call_mcp_tool(yahoo_url, "get_stock_info", ticker="AAPL")
        
        if isinstance(result, dict) and "currentPrice" in result:
             print(f"✅ Success! AAPL Price: ${result['currentPrice']}")
             print(f"   Name: {result.get('shortName')}")
        else:
             print(f"⚠️ Unexpected format: {str(result)[:100]}")
             
        # Test 2: Financials (Heavier payload)
        print("   Fetching AAPL financials...")
        fin_result = await call_mcp_tool(yahoo_url, "get_financials", ticker="AAPL")
        if isinstance(fin_result, dict) and "income_statement" in fin_result:
            print("✅ Success! Retrieved Income Statement.")
        else:
            print(f"⚠️ Unexpected format for financials.")

    except Exception as e:
        print(f"❌ Connection Failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(verify_mcp_standalone())
