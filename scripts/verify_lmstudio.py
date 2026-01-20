import asyncio
import logging
from langchain_core.messages import HumanMessage
from src.agents.graph import app
from src.utils.tracing import setup_tracing

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_verification():
    print("🚀 Verifying DeepAgents with LM Studio (Local)...")
    setup_tracing()
    
    # Analyze AAPL (Liquid, well-known, good for testing tools)
    query = "Analyze AAPL. Check its fundamentals and recent news sentiment."
    print(f"Query: {query}")
    
    initial_state = {
        "messages": [HumanMessage(content=query)]
    }
    
    print("\n⏳ Running Agent Graph...")
    async for event in app.astream(initial_state):
        for node, values in event.items():
            print(f"\n🔹 Node: {node}")
            print(f"🔸 Type: {type(values)}")
            
            # Extract value from Overwrite object if present
            if hasattr(values, "value"):
                values = values.value
                print(f"🔸 Extracted .value -> Type: {type(values)}")

            try:
                if isinstance(values, dict) and "messages" in values:
                    msgs = values["messages"]
                    # Unwrap Overwrite object if present
                    if hasattr(msgs, "value"):
                        msgs = msgs.value
                    
                    if isinstance(msgs, list) and len(msgs) > 0:
                        # Print the last message from the node
                        last_msg = msgs[-1]
                        content = getattr(last_msg, "content", str(last_msg))
                        print(f"📝 {type(last_msg).__name__}: {content[:200]}..." if len(content) > 200 else f"📝 {content}")
                    
                # Check for DeepAgents specific keys
                if isinstance(values, dict) and "deep_agent_state" in values:
                    print("✅ DeepAgents State Updated")
            except Exception as e:
                print(f"⚠️ Error processing node output: {e}")
                print(f"RAW VALUES: {values}")

    print("\n✅ Verification Complete.")

if __name__ == "__main__":
    asyncio.run(run_verification())
