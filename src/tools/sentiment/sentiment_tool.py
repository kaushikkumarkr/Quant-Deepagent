
from newsapi import NewsApiClient
from typing import Dict, Any, List
import datetime
import os
from src.utils.cache import disk_cache
from src.utils.retry import with_retry
from src.utils.logging import setup_logging

logger = setup_logging(__name__)

class SentimentTool:
    """
    Tool for fetching news and sentiment analysis.
    """

    @staticmethod
    def get_client():
        api_key = os.getenv("NEWS_API_KEY")
        if not api_key:
            raise ValueError("NEWS_API_KEY not found in environment")
        return NewsApiClient(api_key=api_key)

    @staticmethod
    @disk_cache(expire=3600)  # 1h cache
    @with_retry(max_attempts=3)
    def get_news_sentiment(ticker: str, days: int = 7) -> List[Dict[str, Any]]:
        """
        Get recent news articles for a ticker.
        """
        try:
            news_api = SentimentTool.get_client()
            end_date = datetime.date.today()
            start_date = end_date - datetime.timedelta(days=days)
            
            articles = news_api.get_everything(
                q=ticker,
                from_param=start_date.isoformat(),
                to=end_date.isoformat(),
                language='en',
                sort_by='relevancy',
                page_size=10
            )
            
            if not articles or 'articles' not in articles:
                return []
                
            results = []
            for article in articles['articles']:
                results.append({
                    "title": article['title'],
                    "source": article['source']['name'],
                    "publishedAt": article['publishedAt'],
                    "description": article['description'],
                    "url": article['url']
                })
                
            return results
        except Exception as e:
            logger.error(f"Error fetching news for {ticker}: {e}")
            return []

    @staticmethod
    def get_reddit_sentiment(ticker: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent Reddit sentiment (Mock).
        """
        # Mocking for now as per legacy implementation
        return [
            {"title": f"{ticker} is looking bullish", "score": 150, "sentiment": "positive"},
            {"title": f"Concerns about {ticker} earnings", "score": 85, "sentiment": "negative"},
            {"title": f"{ticker} technical analysis", "score": 40, "sentiment": "neutral"},
        ]
