import asyncio
import logging
from src.agents.graph import app
from src.agents.state import ResearchState

# Configure logging to see what's happening
logging.basicConfig(level=logging.INFO)

async def main():
    print("Locked & Loaded: Verifying Full Research Graph with MCP Servers...")
    
    # Mock State
    initial_state = {
        "ticker": "AAPL",
    }
    
    print(f"\nrunning research graph for {initial_state['ticker']}...")
    try:
        # Run the graph
        final_state = await app.ainvoke(initial_state)
        
        print("\n--- RESULT ---")
        if "final_report" in final_state:
            print("SUCCESS: Report generated.")
            print("\n=== FINAL REPORT ===\n")
            print(final_state['final_report'])
            print("\n====================\n")
        elif "draft_report" in final_state:
             print("PARTIAL SUCCESS: Draft generated (Critique might have failed or been skipped).")
             print(final_state['draft_report'])
        else:
            print(f"FAILED: No report in final state. Keys: {final_state.keys()}")
            
    except Exception as e:
        print(f"\nCRITICAL FAILURE: {e}")

if __name__ == "__main__":
    asyncio.run(main())
