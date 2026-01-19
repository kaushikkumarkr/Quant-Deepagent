import asyncio
import logging
import sys
import json
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from src.llm.router import router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Define the planning tool manually for testing
@tool
def write_todos(todos: list[str]):
    """
    Create a prioritized list of tasks (todos) for the research agent.
    
    Args:
        todos: List of tasks to be completed.
    """
    return "Tasks saved."

async def main():
    print("🚀 Verifying Planning Capability (Direct LLM Test)...")
    
    llm = router.get_llm()
    if not llm:
        print("❌ No LLM available.")
        return

    # Bind the tool to the LLM
    llm_with_tools = llm.bind_tools([write_todos])
    
    print(f"🔹 Model: {llm.model_name}")
    print("🔹 Instruction: 'Analyze AAPL. First create a plan with write_todos.'")
    
    messages = [
        SystemMessage(content="You are a helpful research assistant. Always plan before executing."),
        HumanMessage(content="Analyze AAPL. First create a plan with specific steps using the write_todos tool.")
    ]
    
    try:
        response = await llm_with_tools.ainvoke(messages)
        print("\n🔹 Response received:")
        
        if response.tool_calls:
            for tool_call in response.tool_calls:
                print(f"🛠️  TOOL CALL: {tool_call['name']}")
                print(f"    Args: {tool_call['args']}")
                if tool_call['name'] == 'write_todos':
                     print("✅ SUCCESS: The LLM correctly generated a planning tool call!")
        else:
            print("⚠️  No tool calls. Content:", response.content)
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
