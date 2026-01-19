import asyncio
import logging
import sys
from src.utils.mcp_client import call_mcp_tool
from pprint import pprint

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

async def test_amd_metrics():
    print(f"\n{'='*60}")
    print("QUERY 1: 'What is the P/E ratio and market cap of AMD?'")
    print(f"{'='*60}")
    try:
        # P/E and Market Cap come from get_stock_info
        info = await call_mcp_tool("src/mcp_servers/yahoo_finance.py", "get_stock_info", ticker="AMD")
        
        if "error" in info:
             print(f"❌ Error: {info['error']}")
        else:
             print("✅ Data Retrieved from Yahoo Finance MCP:")
             print(f"   Ticker: {info.get('symbol')}")
             # P/E might be 'trailingPE' or 'forwardPE'
             print(f"   Trailing P/E: {info.get('trailingPE')}")
             print(f"   Forward P/E:  {info.get('forwardPE')}")
             
             # Market Cap
             mcap = info.get('marketCap')
             if mcap:
                 mcap_formatted = f"${mcap / 1e9:.2f} Billion"
             else:
                 mcap_formatted = "N/A"
             print(f"   Market Cap:   {mcap_formatted}")
                 
    except Exception as e:
        print(f"❌ Exception: {e}")

async def test_apple_health():
    print(f"\n{'='*60}")
    print("QUERY 2: 'How is Apple's financial health considering recent earnings?'")
    print(f"{'='*60}")
    try:
        # Needs Financials and Earnings
        print(">> Fetching Financials...")
        financials = await call_mcp_tool("src/mcp_servers/yahoo_finance.py", "get_financials", ticker="AAPL")
        print(">> Fetching Earnings...")
        earnings = await call_mcp_tool("src/mcp_servers/yahoo_finance.py", "get_earnings", ticker="AAPL")

        print("✅ Data Retrieved:")
        if isinstance(financials, dict) and 'income_statement' in financials:
             is_stmt = financials.get('income_statement', {})
             # Just show we have data, usually it's a list or dict of years
             print(f"   Financials: Available (Keys: {list(is_stmt.keys())[:3]}...)")
        
        if isinstance(earnings, dict) and 'earningss' in earnings: # Note: 'earningss' typo in some yfinance versions or tool wrapper
             earn_data = earnings.get('earningss') or earnings.get('earnings') or earnings
             print(f"   Earnings Data: Available")
             print(f"   Sample: {str(earn_data)[:100]}...")
             
    except Exception as e:
        print(f"❌ Exception: {e}")

async def test_msft_breakdown():
    print(f"\n{'='*60}")
    print("QUERY 3: 'Give me a fundamental breakdown of Microsoft.'")
    print(f"{'='*60}")
    try:
        # Detailed breakdown usually needs Info + Financials
        info = await call_mcp_tool("src/mcp_servers/yahoo_finance.py", "get_stock_info", ticker="MSFT")
        
        print("✅ Data Retrieved (Fundamental Snapshot):")
        print(f"   Company: {info.get('shortName')}")
        print(f"   Sector: {info.get('sector')}")
        print(f"   Price: {info.get('currentPrice')}")
        print(f"   52 Week High: {info.get('fiftyTwoWeekHigh')}")
        print(f"   Beta: {info.get('beta')}")
        print(f"   Revenue Growth: {info.get('revenueGrowth')}")
        print(f"   Profit Margins: {info.get('profitMargins')}")

    except Exception as e:
        print(f"❌ Exception: {e}")

async def main():
    print("🚀 TESTING USER QUERIES VIA RAW MCP (Bypassing LLM for speed)")
    await test_amd_metrics()
    await test_apple_health()
    await test_msft_breakdown()

if __name__ == "__main__":
    asyncio.run(main())
