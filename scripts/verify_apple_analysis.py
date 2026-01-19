import asyncio
import logging
import sys
from src.agents.subagents.fundamentals_agent import fundamentals_agent_node

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

async def main():
    print(f"\n{'='*60}")
    print("🚀 GENERATING FULL ANALYSIS: Apple Financial Health (AAPL)")
    print(f"{'='*60}")
    
    state = {"ticker": "AAPL"}
    
    print("\n🔹 Step 1: Fetching Data via MCP (Yahoo/FRED)...")
    # This calls the agent node, which:
    # 1. Calls MCP tools to get raw numbers
    # 2. Sends those numbers to the LLM to write the report
    try:
        result = await fundamentals_agent_node(state)
        
        print("\n🔹 Step 2: LLM Analysis Generated!")
        print(f"{'='*60}\n")
        
        analysis = result.get("fundamentals_data", {}).get("analysis")
        if not analysis:
             # Fallback if structure is different
             analysis = result.get("analysis", "No analysis found.")
             
        print(analysis)
        print(f"\n{'='*60}")

    except Exception as e:
        print(f"❌ Generation Failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
