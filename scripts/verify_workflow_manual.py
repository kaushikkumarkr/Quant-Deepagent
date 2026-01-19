import asyncio
import logging
import sys
from pprint import pprint

# Import agent nodes
from src.agents.subagents.fundamentals_agent import fundamentals_agent_node
from src.agents.subagents.sentiment_agent import sentiment_agent_node
from src.agents.subagents.forecast_agent import forecast_agent_node

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

async def run_manual_workflow(ticker: str):
    print(f"\n==================================================")
    print(f"🚀 STARTING MANUAL WORKFLOW VERIFICATION: {ticker}")
    print(f"==================================================\n")
    
    # Shared state
    state = {"ticker": ticker}
    reports = {}

    # Step 1: Fundamentals
    print(f"\n🔹 Step 1: calling fundamentals_agent for {ticker}...")
    try:
        res_fund = await fundamentals_agent_node(state)
        reports['fundamentals'] = res_fund.get('analysis', 'No analysis')
        print("✅ Fundamentals Agent Completed.")
    except Exception as e:
        print(f"❌ Fundamentals Failed: {e}")

    # Step 2: Sentiment
    print(f"\n🔹 Step 2: calling sentiment_agent for {ticker}...")
    try:
        res_sent = await sentiment_agent_node(state)
        reports['sentiment'] = res_sent.get('analysis', 'No analysis')
        print("✅ Sentiment Agent Completed.")
    except Exception as e:
        print(f"❌ Sentiment Failed: {e}")

    # Step 3: Forecast
    print(f"\n🔹 Step 3: calling forecast_agent for {ticker}...")
    try:
        res_cast = await forecast_agent_node(state)
        reports['forecast'] = res_cast.get('analysis', 'No analysis')
        print("✅ Forecast Agent Completed.")
    except Exception as e:
        print(f"❌ Forecast Failed: {e}")

    # Step 4: Synthesis (Mocking the Main Agent's final step)
    print(f"\n🔹 Step 4: Synthesizing Final Report...\n")
    
    final_report = f"""
# Investment Research Report: {ticker}

## 1. Fundamental Analysis
{reports.get('fundamentals')}

## 2. Sentiment Analysis
{reports.get('sentiment')}

## 3. Forecast & Technicals
{reports.get('forecast')}

## Conclusion
(This report was synthesized from the outputs of 3 autonomous sub-agents running via MCP)
"""
    print(final_report)
    print("\n🏁 WORKFLOW VERIFICATION COMPLETE")

async def main():
    await run_manual_workflow("NVDA")

if __name__ == "__main__":
    asyncio.run(main())
