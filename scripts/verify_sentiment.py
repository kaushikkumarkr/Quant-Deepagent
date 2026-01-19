import asyncio
import logging
from src.agents.subagents.sentiment_agent import sentiment_agent_node
from src.agents.state import ResearchState

# Configure logging to see what's happening
logging.basicConfig(level=logging.INFO)

async def main():
    print("Locked & Loaded: Verifying Sentiment Agent with MCP Servers...")
    
    # Mock State
    state = {
        "ticker": "AAPL",
    }
    
    print(f"\nrunning sentiment_agent_node for {state['ticker']}...")
    try:
        result = await sentiment_agent_node(state)
        
        print("\n--- RESULT ---")
        if "sentiment_data" in result:
            data = result["sentiment_data"]
            if "error" in data:
                 print(f"FAILED: Agent returned error: {data['error']}")
            else:
                print("SUCCESS: Data retrieved.")
                news = data.get('raw_news')
                reddit = data.get('raw_reddit')
                print(f"News Count: {len(news) if isinstance(news, list) else 'N/A'}")
                print(f"Reddit Count: {len(reddit) if isinstance(reddit, list) else 'N/A'}")
                print(f"Analysis: {data.get('analysis')}")
        else:
            print(f"FAILED: Unexpected result format: {result}")
            
    except Exception as e:
        print(f"\nCRITICAL FAILURE: {e}")

if __name__ == "__main__":
    asyncio.run(main())
