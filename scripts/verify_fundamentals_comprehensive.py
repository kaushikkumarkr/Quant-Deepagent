import asyncio
import logging
from src.agents.subagents.fundamentals_agent import fundamentals_agent_node
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
    print(f"TESTING FUNDAMENTALS AGENT: {ticker}")
    print(f"{'='*50}")
    
    state = {"ticker": ticker}
    
    try:
        result = await fundamentals_agent_node(state)
        
        if "fundamentals_data" in result:
            data = result["fundamentals_data"]
            if "error" in data:
                print(f"❌ FAILED: Agent returned error: {data['error']}")
            else:
                raw = data.get('raw_info', {})
                print(f"✅ SUCCESS: Data retrieved for {ticker}")
                print(f"   - Name: {raw.get('shortName', 'N/A')}")
                print(f"   - Sector: {raw.get('sector', 'N/A')}")
                print(f"   - Market Cap: {raw.get('marketCap', 'N/A')}")
                print(f"   - Current Price: {raw.get('currentPrice', 'N/A')}")
                
                analysis = data.get('analysis')
                if analysis:
                    print(f"\n   📝 LLM Analysis Summary:")
                    # Print first few lines of analysis to verify content
                    print(f"   {str(analysis)[:300]}...")
                else:
                     print(f"   ⚠️ WARNING: No LLM analysis generated.")
        else:
            print(f"❌ FAILED: Unexpected result keys: {result.keys()}")
            
    except Exception as e:
        print(f"❌ CRITICAL EXCEPTION: {e}")

async def main():
    test_cases = ["AAPL", "TSLA", "NVDA"]
    
    print("🚀 Starting Comprehensive Fundamentals Verification...")
    for ticker in test_cases:
        await test_ticker(ticker)
        # Small pause between agents if needed, though they run sequentially here
        await asyncio.sleep(2)
        
    print("\n🏁 Verification Complete.")

if __name__ == "__main__":
    asyncio.run(main())
