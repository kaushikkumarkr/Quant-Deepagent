import asyncio
import logging
from langchain_core.messages import HumanMessage
from src.llm.router import router
from src.utils.tracing import setup_tracing

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    print("🚀 Verifying Connectivity & Tracing...")
    
    # 1. Setup Tracing
    phoenix_url = setup_tracing()
    if phoenix_url:
        print(f"✅ Arize Phoenix UI: {phoenix_url}")
    else:
        print("⚠️ Phoenix tracing failed to initialize")

    # 2. Get LLM (LM Studio)
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

    # 3. Simple Generation
    print("\n⏳ Testing Generation (Simple 'Hello')...")
    try:
        response = await llm.ainvoke([HumanMessage(content="Hello! Are you ready?")])
        print(f"✅ Response received:\n   {response.content}")
        print("\n✅ Connectivity Check Passed!")
        print("   Check Phoenix UI for the trace of this call.")
        
    except Exception as e:
        print(f"❌ Generation Failed: {e}")

    # 4. Test Dockerized MCP Server
    print("\n🛠️  Testing Dockerized MCP Server (Yahoo Finance)...")
    try:
        from src.utils.mcp_client import call_mcp_tool
        import os
        
        yahoo_url = os.getenv("YAHOO_MCP_URL")
        print(f"   Using YAHOO_MCP_URL: {yahoo_url}")
        
        if yahoo_url and yahoo_url.startswith("http"):
             print(f"   Connecting to SSE endpoint: {yahoo_url}")
             # We use AAPL as a test ticker
             result = await call_mcp_tool(yahoo_url, "get_stock_info", ticker="AAPL")
             if isinstance(result, str):
                 print(f"✅ Raw Result: {result[:100]}...")
             else:
                 print(f"✅ Parsed Result: {result.get('symbol')} Price: {result.get('currentPrice')}")
        else:
            print("⚠️  YAHOO_MCP_URL not set or not http, skipping specific SSE test.")
            
    except Exception as e:
        print(f"❌ MCP Test Failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
