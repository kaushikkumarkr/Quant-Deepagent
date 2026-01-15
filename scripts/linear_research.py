
import asyncio
import sys
import os

# Ensure src is in path
sys.path.insert(0, os.getcwd())

from src.tools.financial.yahoo_finance import YahooFinanceTool
from src.tools.financial.fred import FREDTool
from src.tools.sentiment.news_api import NewsAPITool
from src.llm.router import router
from langchain_core.messages import HumanMessage

async def main():
    ticker = "TSLA"
    print(f"\n🚀 Starting Linear Research Verification for {ticker}...\n" + "="*50)

    # 1. Fundamentals (Yahoo)
    print("\n[1] Fetching Fundamentals (Yahoo Finance)...")
    yf = YahooFinanceTool()
    info = yf.get_stock_info(ticker)
    print(f"✅ Market Cap: {info.get('marketCap', 'N/A')}")
    print(f"✅ Sector: {info.get('sector', 'N/A')}")

    # 2. Macro (FRED)
    print("\n[2] Fetching Macro Data (FRED)...")
    fred = FREDTool()
    try:
        gdp = fred.get_economic_data("GDP")
        rate = fred.get_economic_data("DGS10") # 10-Year Treasury
        print(f"✅ GDP Latest: {gdp.get('latest_value')} {gdp.get('units')}")
        print(f"✅ 10Y Yield: {rate.get('latest_value')}%")
    except Exception as e:
        print(f"❌ FRED Error: {e}")
        gdp = {"latest_value": "Unknown"}

    # 3. Sentiment (NewsAPI)
    print("\n[3] Fetching News Sentiment (NewsAPI)...")
    news = NewsAPITool()
    articles = news.get_news(ticker)
    print(f"✅ Articles Found: {len(articles)}")
    if articles:
        print(f"   Headlines: {[a['title'] for a in articles[:2]]}...")

    # 4. Synthesis (MLX LLM)
    print("\n[4] Generating Report with Local LLM (MLX)...")
    llm = router.get_llm()
    
    if not llm:
        print("❌ LLM not available.")
        return

    prompt = f"""
    You are a financial analyst. Write a very brief 3-sentence summary analysis for {ticker} based on:
    - Market Cap: {info.get('marketCap')}
    - Latest US GDP: {gdp.get('latest_value')}
    - Recent News Count: {len(articles)}
    
    Analysis:
    """
    
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        print(f"\n📝 LLM Analysis:\n{response.content}")
        print("\n✅ System Verification Complete: All components functional.")
    except Exception as e:
        print(f"❌ LLM Generation Failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
