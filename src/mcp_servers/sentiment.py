from fastmcp import FastMCP
from newsapi import NewsApiClient
from typing import Dict, Any, List
import datetime
import sys
import os
import warnings

# Suppress warnings
warnings.filterwarnings("ignore")

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.config import settings

# Initialize FastMCP Server
mcp = FastMCP("sentiment-analysis")

def get_news_client():
    if not settings.news_api_key:
        raise ValueError("NewsAPI Key not found.")
    return NewsApiClient(api_key=settings.news_api_key)

@mcp.tool()
def get_news_sentiment(ticker: str, days: int = 7) -> str:
    """
    Get recent news articles and simple sentiment for a ticker.
    """
    try:
        news_api = get_news_client()
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
            return "No news found."
            
        results = []
        for article in articles['articles']:
            results.append({
                "title": article['title'],
                "source": article['source']['name'],
                "publishedAt": article['publishedAt'],
                "description": article['description'],
                "url": article['url']
            })
            
        return str(results)
    except Exception as e:
        return f"Error fetching news for {ticker}: {e}"

@mcp.tool()
def get_reddit_sentiment(ticker: str, limit: int = 10) -> str:
    """
    Get recent Reddit sentiment (Mock implementation as placehoder).
    Real implementation would use PRAW.
    """
    # Mock data for now as per plan to fix the "bug" of missing reddit
    mock_data = [
        {"title": f"{ticker} is looking bullish", "score": 150, "sentiment": "positive"},
        {"title": f"Concerns about {ticker} earnings", "score": 85, "sentiment": "negative"},
        {"title": f"{ticker} technical analysis", "score": 40, "sentiment": "neutral"},
    ]
    return str(mock_data)

if __name__ == "__main__":
    mcp.run()
