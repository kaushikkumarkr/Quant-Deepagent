import asyncio
import sys
from src.agents.graph import app
from langchain_core.messages import HumanMessage

async def run_demo(ticker: str):
    print(f"\n🚀 Starting QuantMind Research Agent for {ticker}...\n")
    print("-" * 50)
    
    # Initialize state
    initial_state = {
        "ticker": ticker,
        "messages": [HumanMessage(content=f"Research {ticker} and write a report.")]
    }
    
    # Run the graph
    # DeepAgents graph invocation
    try:
        # Note: app.invoke might return a generator or final state depending on config.
        # For DeepAgents/LangGraph, invoke typically returns final state.
        result = await app.invoke(initial_state)
        
        print("\n✅ Research Complete!")
        print("-" * 50)
        
        # Extract Final Report (Logic depends on deepagents internal state structure)
        # DeepAgents often puts the final response in the messages or specific key
        
        # Let's inspect the keys to find the report
        if isinstance(result, dict):
            # Try to match our ResearchState or DeepAgents state
            if "final_report" in result:
                print("\n📄 FINAL REPORT:\n")
                print(result["final_report"])
            elif "messages" in result:
                last_msg = result["messages"][-1]
                print("\n💬 Final Agent Message:\n")
                print(last_msg.content)
            else:
                print(f"\n⚠️ Unexpected State Keys: {result.keys()}")
                
    except Exception as e:
        print(f"\n❌ Agent Execution Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    ticker = sys.argv[1] if len(sys.argv) > 1 else "TSLA"
    asyncio.run(run_demo(ticker))
