import asyncio
import logging
import sys
import json
import ast
from src.utils.mcp_client import call_mcp_tool
from pprint import pprint

# Configure logging to stdout
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

async def verify_yahoo():
    print(f"\n{'='*50}")
    print("VERIFYING YAHOO FINANCE MCP")
    print(f"{'='*50}")
    try:
        print(">> Calling get_stock_info(ticker='NVDA')...")
        result = await call_mcp_tool("src/mcp_servers/yahoo_finance.py", "get_stock_info", ticker="NVDA")
        if isinstance(result, dict) and "error" in result:
             print(f"❌ Error: {result['error']}")
        else:
             print("✅ Success! Data received:")
             # Yahoo returns a dict directly usually, but let's be safe
             if isinstance(result, str):
                 try:
                     result = ast.literal_eval(result)
                 except:
                     pass
             
             if isinstance(result, dict):
                 print(f"   Symbol: {result.get('symbol')}")
                 print(f"   Current Price: {result.get('currentPrice') or result.get('regularMarketPrice')}")
                 print(f"   Sector: {result.get('sector')}")
             else:
                 print(f"   Raw Result: {str(result)[:100]}...")
    except Exception as e:
        print(f"❌ Exception: {e}")

async def verify_fred():
    print(f"\n{'='*50}")
    print("VERIFYING FRED MCP")
    print(f"{'='*50}")
    try:
        print(">> Calling get_economic_data(series_id='GDP')...")
        result = await call_mcp_tool("src/mcp_servers/fred.py", "get_economic_data", series_id="GDP")
        if isinstance(result, dict) and "error" in result:
             print(f"❌ Error: {result['error']}")
        else:
             print("✅ Success! Data received:")
             if isinstance(result, str):
                 try:
                     result = ast.literal_eval(result)
                 except:
                     pass

             if isinstance(result, dict):
                 print(f"   Series ID: {result.get('series_id')}")
                 data_points = result.get('data', {})
                 print(f"   Data Points: {len(data_points)} points retrieved")
                 if data_points:
                    print(f"   Latest Value: {list(data_points.values())[-1]}")
             else:
                 print(f"   Raw Result: {str(result)[:100]}...")
    except Exception as e:
        print(f"❌ Exception: {e}")

async def verify_sentiment():
    print(f"\n{'='*50}")
    print("VERIFYING SENTIMENT MCP")
    print(f"{'='*50}")
    try:
        print(">> Calling get_news_sentiment(ticker='NVDA')...")
        # FIXED: Use 'ticker' instead of 'query'
        result = await call_mcp_tool("src/mcp_servers/sentiment.py", "get_news_sentiment", ticker="NVDA")
        
        if isinstance(result, dict) and "error" in result:
             print(f"❌ Error: {result['error']}")
        else:
             print("✅ Success! Data received:")
             # Parse string result
             try:
                 if isinstance(result, str):
                     articles = ast.literal_eval(result)
                 else:
                     articles = result
                 
                 if isinstance(articles, list):
                     print(f"   Articles Found: {len(articles)}")
                     if articles:
                         print(f"   First Article Title: {articles[0].get('title')}")
                 else:
                     print(f"   Raw Result: {str(articles)[:100]}...")
             except Exception as parse_err:
                 print(f"   Could not parse result: {str(result)[:100]}...")
    except Exception as e:
        print(f"❌ Exception: {e}")

async def verify_forecast():
    print(f"\n{'='*50}")
    print("VERIFYING FORECAST MCP")
    print(f"{'='*50}")
    try:
        print(">> Calling forecast_price(ticker='NVDA', periods=30)...")
        # FIXED: Use 'periods' instead of 'days'
        result = await call_mcp_tool("src/mcp_servers/forecast.py", "forecast_price", ticker="NVDA", periods=30)
        
        if isinstance(result, dict) and "error" in result:
             print(f"❌ Error: {result['error']}")
        else:
             print("✅ Success! Data received:")
             # Parse string result
             try:
                 if isinstance(result, str):
                     # Replace nan with None for parsing if valid JSON-ish
                     clean_result = result.replace('nan', 'None')
                     data = ast.literal_eval(clean_result)
                 else:
                     data = result
                 
                 if isinstance(data, dict):
                     print(f"   Ticker: {data.get('ticker')}")
                     print(f"   Current Price: {data.get('current_price')}")
                     print(f"   Forecast 30d: {data.get('forecast_price_30d')}")
                     forecast_data = data.get('forecast_data', [])
                     print(f"   Forecast Data Points: {len(forecast_data)}")
                 else:
                      print(f"   Raw Result: {str(data)[:100]}...")
             except Exception as parse_err:
                  print(f"   Raw Result (Unparsed): {str(result)[:200]}...")

    except Exception as e:
        print(f"❌ Exception: {e}")

async def main():
    print("🚀 STARTING RAW MCP VERIFICATION (No LLM)")
    await verify_yahoo()
    await verify_fred()
    await verify_sentiment()
    await verify_forecast()
    print("\n🏁 RAW VERIFICATION COMPLETE")

if __name__ == "__main__":
    asyncio.run(main())
