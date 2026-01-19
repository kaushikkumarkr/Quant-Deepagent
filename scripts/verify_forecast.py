import asyncio
import logging
from src.agents.subagents.forecast_agent import forecast_agent_node
from src.agents.state import ResearchState

# Configure logging to see what's happening
logging.basicConfig(level=logging.INFO)

async def main():
    print("Locked & Loaded: Verifying Forecast Agent with MCP Servers...")
    
    # Mock State
    state = {
        "ticker": "AAPL",
    }
    
    print(f"\nrunning forecast_agent_node for {state['ticker']}...")
    try:
        result = await forecast_agent_node(state)
        
        print("\n--- RESULT ---")
        if "forecast_data" in result:
            data = result["forecast_data"]
            if "error" in data:
                 print(f"FAILED: Agent returned error: {data['error']}")
            else:
                print("SUCCESS: Data retrieved.")
                fcst = data.get('raw_forecast')
                tech = data.get('raw_indicators')
                print(f"Prophet Data: {list(fcst.keys()) if isinstance(fcst, dict) else fcst}")
                print(f"Technical Signals: {tech.get('signals') if isinstance(tech, dict) else tech}")
                print(f"Analysis: {data.get('analysis')}")
        else:
            print(f"FAILED: Unexpected result format: {result}")
            
    except Exception as e:
        print(f"\nCRITICAL FAILURE: {e}")

if __name__ == "__main__":
    asyncio.run(main())
