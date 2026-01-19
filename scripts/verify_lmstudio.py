import asyncio
from src.llm.router import router
from langchain_core.messages import HumanMessage

async def main():
    print("Checking LLM Router Health...")
    health = router.check_health()
    print(f"Health: {health}")
    
    if not health.get("lmstudio"):
        print("ERROR: LM Studio is not available. Please ensure it is running at http://127.0.0.1:1234")
        return

    print("\nAttempting to invoke LM Studio...")
    try:
        llm = router.get_llm()
        response = llm.invoke([HumanMessage(content="Hello! Are you working?")])
        print(f"\nResponse from LLM:\n{response.content}")
        print("\nSUCCESS: Connected to LM Studio!")
    except Exception as e:
        print(f"\nERROR: Failed to invoke LLM: {e}")

if __name__ == "__main__":
    asyncio.run(main())
