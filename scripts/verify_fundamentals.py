import asyncio
import logging
from src.agents.subagents.fundamentals_agent import fundamentals_agent_node
from src.agents.state import ResearchState

# Configure logging to see what's happening
logging.basicConfig(level=logging.INFO)

async def main():
    print("Locked & Loaded: Verifying Fundamentals Agent with MCP Servers...")
    
    # Mock State
    state = {
        "ticker": "AAPL",  # Apple is a good test case
    }
    
    print(f"\nrunning fundamentals_agent_node for {state['ticker']}...")
    try:
        result = await fundamentals_agent_node(state)
        
        print("\n--- RESULT ---")
        if "fundamentals_data" in result:
            data = result["fundamentals_data"]
            if "error" in data:
                 print(f"FAILED: Agent returned error: {data['error']}")
            else:
                print("SUCCESS: Data retrieved.")
                print(f"Raw Info Keys: {list(data.get('raw_info', {}).keys())}")
                print(f"Analysis: {data.get('analysis')}")
        else:
            print(f"FAILED: Unexpected result format: {result}")
            
    except Exception as e:
        print(f"\nCRITICAL FAILURE: {e}")

if __name__ == "__main__":
    asyncio.run(main())
