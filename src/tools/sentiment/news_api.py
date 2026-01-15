from newsapi import NewsApiClient
from typing import List, Dict, Any
from src.config import settings
from src.utils.cache import disk_cache
from src.utils.retry import with_retry
from src.utils.logging import setup_logging
from datetime import datetime, timedelta

logger = setup_logging(__name__)

class NewsAPITool:
    """
    Tool for fetching news using NewsAPI.org.
    """
    
    def __init__(self):
        self.api_key = settings.news_api_key
        self.client = None
        if self.api_key:
            self.client = NewsApiClient(api_key=self.api_key)
        else:
            logger.warning("NewsAPI Key not found.")

    @disk_cache(expire=3600)
    @with_retry(max_attempts=3)
    def get_news(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent news articles (last 7 days).
        """
        if not self.client:
            return [{"error": "API Key missing"}]
            
        try:
            from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            
            response = self.client.get_everything(
                q=query,
                from_param=from_date,
                language='en',
                sort_by='relevancy',
                page_size=limit
            )
            
            articles = response.get('articles', [])
            return [
                {
                    "title": a['title'],
                    "description": a['description'],
                    "url": a['url'],
                    "source": a['source']['name'],
                    "publishedAt": a['publishedAt'],
                    "content": a['content']
                }
                for a in articles
            ]
            
        except Exception as e:
            logger.error(f"NewsAPI failed: {e}")
            return [{"error": str(e)}]
