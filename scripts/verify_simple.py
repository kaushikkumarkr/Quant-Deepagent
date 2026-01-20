import asyncio
import logging
from langchain_core.messages import HumanMessage
# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    print("🚀 Verifying LM Studio Connectivity (Without Phoenix)...")
    print("⏳ Importing modules (this may take a moment)...")
    from src.llm.router import router

    
    # 1. Get LLM (LM Studio)
    try:
        llm = router.get_llm()
        if not llm:
            print("❌ Failed to get LLM from router")
            return
            
        print(f"✅ Connected to LLM Provider: {llm.__class__.__name__}")
        if hasattr(llm, 'base_url'):
            print(f"   URL: {llm.base_url}")
            
    except Exception as e:
        print(f"❌ LLM Router Error: {e}")
        return

    # 2. Simple Generation
    print("\n⏳ Testing Generation (Simple 'Hello')...")
    try:
        response = await llm.ainvoke([HumanMessage(content="Hello! Are you ready?")])
        print(f"✅ Response received:\n   {response.content}")
        print("\n✅ LM Studio Connectivity Check Passed!")
        
    except Exception as e:
        print(f"❌ Generation Failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
