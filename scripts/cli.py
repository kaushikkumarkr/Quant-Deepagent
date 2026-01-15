
import asyncio
import sys
import os

# Ensure src is in path
sys.path.insert(0, os.getcwd())

from src.agents.graph import create_graph
from langchain_core.messages import HumanMessage

async def main():
    print("🚀 QuantMind CLI - Interactive Research Agent")
    print("Type 'exit' or 'quit' to stop.")
    print("-" * 50)
    
    # Initialize Graph
    print("⏳ Initializing Agent Graph...")
    try:
        app = create_graph()
        print("✅ Agent Ready.\n")
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        return

    while True:
        user_input = input("Enter ticker or query (e.g., 'Analyze NVDA'): ").strip()
        
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break
            
        if not user_input:
            continue

        print(f"\n🕵️‍♂️ Researching: {user_input}...\n")
        
        try:
            # Create initial state
            initial_state = {
                "messages": [HumanMessage(content=user_input)]
            }
            
            # Stream events
            # Note: DeepAgents/LangGraph streaming can be verbose. 
            # We'll try to print the final response or key steps.
            
            final_response = None
            async for event in app.astream(initial_state):
                # Print everything for debugging visibility
                for key, value in event.items():
                    print(f"\n🔹 Step: {key}")
                    # DeepAgents returns various types; handle gracefully
                    if isinstance(value, dict) and "messages" in value:
                        messages = value["messages"]
                        if isinstance(messages, list):
                            for msg in messages:
                                if hasattr(msg, "content") and msg.content:
                                    print(f"📝 Content: {msg.content[:500]}...")
                                if hasattr(msg, "tool_calls") and msg.tool_calls:
                                    for tc in msg.tool_calls:
                                        print(f"🛠️  Call: {tc['name']} ({tc['args']})")
                        else:
                            print(f"   {messages}")
                    else:
                        print(f"   {type(value).__name__}: {str(value)[:200]}")
                         
            print("-" * 50)
            
        except Exception as e:
            print(f"❌ Error during execution: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
