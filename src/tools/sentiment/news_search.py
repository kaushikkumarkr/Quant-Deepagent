from typing import Dict, Any, List
from src.tools.search.web_search import WebSearchTool
from src.tools.sentiment.finbert import FinBERT
from src.utils.cache import disk_cache
from src.utils.logging import setup_logging

logger = setup_logging(__name__)

class NewsSentimentTool:
    """
    Combines Web Search and FinBERT to provide market sentiment analysis.
    """
    
    def __init__(self):
        self.search_tool = WebSearchTool()
        self.finbert = FinBERT()

    @disk_cache(expire=3600)
    def analyze_ticker_news(self, ticker: str, limit: int = 10) -> Dict[str, Any]:
        """
        Search for news about a ticker and analyze sentiment.
        """
        logger.info(f"Analyzing news sentiment for {ticker}...")
        
        # 1. Search for news
        queries = [
            f"{ticker} stock news",
            f"{ticker} earnings analysis",
            f"{ticker} forecast 2024"
        ]
        
        all_articles = []
        seen_urls = set()
        
        for q in queries:
            results = self.search_tool.search_news(q, limit=5)
            for r in results:
                if r['href'] not in seen_urls:
                    all_articles.append(r)
                    seen_urls.add(r['href'])
        
        if not all_articles:
            return {"error": "No news found", "sentiment_score": 0, "label": "neutral"}
            
        # 2. Extract texts for analysis (Title + Snippet)
        analyze_texts = [f"{a['title']}. {a['body']}" for a in all_articles]
        
        # 3. specific filtering: ignore very short texts
        valid_indices = [i for i, t in enumerate(analyze_texts) if len(t) > 20]
        valid_texts = [analyze_texts[i] for i in valid_indices]
        valid_articles = [all_articles[i] for i in valid_indices]
        
        # 4. Run FinBERT
        sentiment_result = self.finbert.analyze_batch(valid_texts)
        
        # 5. Combine results
        return {
            "ticker": ticker,
            "overall_sentiment": sentiment_result['label'], # bullish/bearish/neutral
            "sentiment_score": sentiment_result['sentiment_score'],
            "article_count": len(valid_articles),
            "distribution": sentiment_result.get("distribution"),
            "top_articles": valid_articles[:5] # Return top 5 for context
        }
