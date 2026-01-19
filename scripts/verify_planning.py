import asyncio
import logging
import sys
from langchain_core.messages import HumanMessage
from src.agents.graph import app

# Configure logging to see tool calls
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

async def main():
    print("🚀 Verifying Main Agent Planning & Delegation...")
    
    # We want to see if the agent calls 'write_todos' (Planning) 
    # and then 'task' (Delegation)
    
    # Explicitly providing a message to avoid "no first user message" error
    initial_state = {
        "ticker": "AAPL",
        "messages": [HumanMessage(content="Analyze AAPL. First create a plan, then execute it.")]
    }
    
    print(f"\nRunning agent with input: {initial_state['messages'][0].content}...")
    try:
        # Run step-by-step to catch the first tool call
        async for event in app.astream(initial_state):
            for key, value in event.items():
                print(f"\n🔹 Agent Step: {key}")
                if "messages" in value:
                    last_msg = value["messages"][-1]
                    if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
                        for tool_call in last_msg.tool_calls:
                            print(f"🛠️  TOOL CALL DETECTED: {tool_call['name']}")
                            print(f"    Args: {tool_call['args']}")
                            
                            if tool_call['name'] == 'write_todos':
                                print("✅ SUCCESS: Agent is PLANNING tasks via write_todos!")
                            elif tool_call['name'] == 'task':
                                print(f"✅ SUCCESS: Agent is DELEGATING to sub-agent: {tool_call['args'].get('subagent_name')}")
    
    except Exception as e:
        print(f"\n❌ Execution Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
