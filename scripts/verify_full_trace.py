import asyncio
import sys
import logging
from langchain_core.messages import HumanMessage
from src.agents.graph import create_graph
from src.utils.observability import setup_observability

# Configure logging
logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler(sys.stdout)])

async def main():
    print("\n🌳 Generating Hierarchical Trace (The 'Tree' View)")
    print("--------------------------------------------------")
    
    # 1. Enable Tracing
    setup_observability()
    
    # 2. Build the actual LangChain Graph
    # This is critical: The Graph object is what LangChain traces as the "Parent"
    app = create_graph()
    
    print("\n🚀 Running 'Analyze NVDA' through the Agent Graph...")
    print("   This will trigger: Main -> Planning -> SubAgents -> Tools")
    
    # 3. Invoke the Graph (Standard LangGraph invocation)
    initial_state = {
        "messages": [HumanMessage(content="Analyze NVDA")]
    }
    
    # We use invoke() to ensure it runs as a single traceable unit
    try:
        # Note: limiting recursion or steps might be needed if it loops, 
        # but for verification default is fine.
        result = await app.ainvoke(initial_state)
        
        print("\n✅ Execution Complete!")
        print("   Check http://localhost:6006 now.")
        print("   You should see a Root Span (LangGraph) with children.")
        
    except Exception as e:
        print(f"❌ Graph Execution Failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
