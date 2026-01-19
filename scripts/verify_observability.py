import asyncio
import sys
import logging
from src.utils.observability import setup_observability

# Configure logging to see the Phoenix output
logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler(sys.stdout)])

async def main():
    print("\n🧪 Testing Arize Phoenix Integration...")
    try:
        setup_observability()
        print("\n✅ Setup call completed successfully.")
        print("   If you see the Phoenix URL above, it is working!")
        print("   Waiting 10 seconds to keep server alive for manual check...")
        await asyncio.sleep(10)
    except Exception as e:
        print(f"❌ Verification Failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
