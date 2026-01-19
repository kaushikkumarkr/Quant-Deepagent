import asyncio
import sys
import logging
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from src.utils.observability import setup_observability, logger as list_logger

# Configure logging
logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler(sys.stdout)])

async def main():
    print("\n🔍 DIAGNOSTIC: Testing Arize Phoenix Tracing")
    
    # 1. Start Observability
    setup_observability()
    
    print("   Server should be running at http://localhost:6006")
    print("   Sending a test LLM call now...")

    # 2. Make a standard LangChain call (should be auto-captured)
    try:
        # Use the same provider config as the app
        llm = ChatOpenAI(
            base_url="http://localhost:1234/v1",
            api_key="lm-studio",
            model="gpt-3.5-turbo",
            temperature=0
        )
        
        msg = HumanMessage(content="What is the capital of France? Answer in one word.")
        response = await llm.ainvoke([msg])
        
        print(f"✅ LLM Response Received: {response.content}")
        print("   -> Check Phoenix 'Traces' tab now.")
        
    except Exception as e:
        print(f"❌ LLM Call Failed: {e}")
        print("   (Ensure LM Studio is running)")

    # 3. Wait to allow flush
    print("⏳ Waiting 5 seconds for traces to flush...")
    await asyncio.sleep(5)
    print("DONE.")

if __name__ == "__main__":
    asyncio.run(main())
