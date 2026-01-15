from typing import List, Dict, Any
from duckduckgo_search import DDGS
from src.utils.logging import setup_logging
from src.utils.retry import with_retry

logger = setup_logging(__name__)

class WebSearchTool:
    """
    Tool for searching the web using DuckDuckGo (free, no API key).
    """
    
    def __init__(self):
        self.ddgs = DDGS()

    @with_retry(max_attempts=3)
    def search_general(self, query: str, limit: int = 5) -> List[Dict[str, str]]:
        """
        Perform a general web search.
        """
        try:
            results = list(self.ddgs.text(query, max_results=limit))
            return [
                {
                    "title": r.get("title", ""),
                    "href": r.get("href", ""),
                    "body": r.get("body", "")
                }
                for r in results
            ]
        except Exception as e:
            logger.error(f"Error searching DDG for {query}: {e}")
            return []

    @with_retry(max_attempts=3)
    def search_news(self, query: str, limit: int = 10) -> List[Dict[str, str]]:
        """
        Perform a news search.
        """
        try:
            results = list(self.ddgs.news(query, max_results=limit))
            return [
                {
                    "title": r.get("title", ""),
                    "href": r.get("url", "") or r.get("href", ""),
                    "body": r.get("body", "") or r.get("snippet", ""),
                    "source": r.get("source", ""),
                    "date": r.get("date", "")
                }
                for r in results
            ]
        except Exception as e:
            logger.error(f"Error searching news for {query}: {e}")
            return []
