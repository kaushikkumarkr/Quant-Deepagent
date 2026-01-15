import sys
import os
import asyncio
from src.config import settings
from src.tools.sentiment.news_api import NewsAPITool
from src.llm.providers.mlx_provider import MLXProvider
from langchain_core.messages import HumanMessage

async def main():
    print("=== QuantMind System Verification (Strict) ===")
    
    # 1. Config Check
    print("\n[1] Checking Configuration...")
    missing = []
    if not settings.news_api_key: missing.append("NEWS_API_KEY")
    # Check if we can proceed without keys? User requested use of them.
    if missing:
        print(f"❌ Missing Keys: {', '.join(missing)}")
        print("Please ensure they are set in .env")
    else:
        print("✅ API Keys present.")

    # 2. Yahoo Finance Check
    print("\n[2] Testing Yahoo Finance...")
    try:
        from src.tools.financial.yahoo_finance import YahooFinanceTool
        yf = YahooFinanceTool()
        profile = yf.get_stock_info("AAPL")
        if profile and "symbol" in profile and profile['symbol'] == 'AAPL':
            print(f"✅ Yahoo Finance Success: AAPL Found")
        else:
            print(f"❌ Yahoo Finance Failed: {profile}")
    except Exception as e:
        print(f"❌ Yahoo Exception: {e}")

    # 3. NewsAPI Check
    print("\n[3] Testing NewsAPI...")
    try:
        news = NewsAPITool()
        articles = news.get_news("NVDA", limit=3)
        if articles and isinstance(articles, list) and len(articles) > 0 and "error" not in articles[0]:
            print(f"✅ NewsAPI Success: Found {len(articles)} articles for NVDA")
            print(f"   Sample: {articles[0]['title'][:50]}...")
        else:
            print(f"❌ NewsAPI Failed: {articles}")
    except Exception as e:
        print(f"❌ NewsAPI Exception: {e}")

    # 4. MLX Check (Strict)
    print("\n[4] Testing Local MLX LLM...")
    provider = MLXProvider()
    if not provider.is_available():
        print("❌ MLX Provider reports NOT AVAILABLE.")
        print("   Ensure you are using the correct venv and on Apple Silicon.")
    else:
        print(f"✅ MLX Available (Model: {provider.model_path}).")
        print("   Generating test response (this may take time to load weights)...")
        try:
            llm = provider.get_llm()
            if llm:
                resp = llm.invoke([HumanMessage(content="Say 'System Verified' and nothing else.")])
                print(f"✅ MLX Response: {resp.content}")
            else:
                print("❌ Failed to initialize ChatMLX.")
        except Exception as e:
            print(f"❌ MLX Generation Exception: {e}")

if __name__ == "__main__":
    if sys.platform != "darwin":
        print("❌ This script is intended for macOS (Apple Silicon).")
        sys.exit(1)
    asyncio.run(main())
