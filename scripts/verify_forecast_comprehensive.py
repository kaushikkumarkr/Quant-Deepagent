import asyncio
import logging
from src.agents.subagents.forecast_agent import forecast_agent_node
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
    print(f"TESTING FORECAST AGENT: {ticker}")
    print(f"{'='*50}")
    
    state = {"ticker": ticker}
    
    try:
        result = await forecast_agent_node(state)
        
        if "forecast_data" in result:
            data = result["forecast_data"]
            if "error" in data:
                print(f"❌ FAILED: Agent returned error: {data['error']}")
            else:
                fcst = data.get('raw_forecast', {})
                tech = data.get('raw_indicators', {})
                
                print(f"✅ SUCCESS: Data retrieved for {ticker}")
                
                # Check Forecast
                if isinstance(fcst, dict) and 'forecast_data' in fcst:
                    print(f"   - Prophet Forecast: Generated {len(fcst['forecast_data'])} days")
                    print(f"   - Current Price: {fcst.get('current_price')}")
                    print(f"   - 30d Target: {fcst.get('forecast_price_30d')}")
                else:
                    print(f"   - Prophet Forecast: Unexpected format {type(fcst)}")

                # Check Technicals
                if isinstance(tech, dict):
                     print(f"   - Signals: {tech.get('signals')}")
                     print(f"   - RSI: {tech.get('current_metrics', {}).get('rsi')}")
                else:
                     print(f"   - Technicals: Unexpected format {type(tech)}")
                
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
    test_cases = ["SPY", "AMD", "GME"]
    
    print("🚀 Starting Comprehensive Forecast Verification...")
    for ticker in test_cases:
        await test_ticker(ticker)
        await asyncio.sleep(2)
        
    print("\n🏁 Verification Complete.")

if __name__ == "__main__":
    asyncio.run(main())
