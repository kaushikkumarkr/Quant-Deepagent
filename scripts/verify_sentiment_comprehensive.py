import asyncio
import logging
from src.agents.subagents.sentiment_agent import sentiment_agent_node
from src.agents.state import ResearchState
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

async def test_ticker(ticker: str):
    print(f"\n\n{'='*50}")
    print(f"TESTING SENTIMENT AGENT: {ticker}")
    print(f"{'='*50}")
    
    state = {"ticker": ticker}
    
    try:
        result = await sentiment_agent_node(state)
        
        if "sentiment_data" in result:
            data = result["sentiment_data"]
            if "error" in data:
                print(f"❌ FAILED/ERROR: Agent returned error (expected for invalid ticker): {data['error']}")
            else:
                news = data.get('raw_news', [])
                reddit = data.get('raw_reddit', [])
                
                print(f"✅ SUCCESS: Data retrieved for {ticker}")
                print(f"   - News Articles: {len(news) if isinstance(news, list) else news}")
                print(f"   - Reddit Posts: {len(reddit) if isinstance(reddit, list) else reddit}")
                
                analysis = data.get('analysis')
                if analysis:
                    print(f"\n   📝 LLM Analysis Summary:")
                    print(f"   {str(analysis)[:300]}...")
                else:
                     print(f"   ⚠️ WARNING: No LLM analysis generated.")
        else:
            print(f"❌ FAILED: Unexpected result keys: {result.keys()}")
            
    except Exception as e:
        print(f"❌ CRITICAL EXCEPTION: {e}")

async def main():
    test_cases = ["AAPL", "MSFT", "INVALID_TICKER"]
    
    print("🚀 Starting Comprehensive Sentiment Verification...")
    for ticker in test_cases:
        await test_ticker(ticker)
        await asyncio.sleep(2)
        
    print("\n🏁 Verification Complete.")

if __name__ == "__main__":
    asyncio.run(main())
