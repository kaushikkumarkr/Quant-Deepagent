
from fastmcp import FastMCP
from src.tools.sentiment.sentiment_tool import SentimentTool

# Create FastMCP server
mcp = FastMCP("sentiment-analysis")

@mcp.tool()
def get_news_sentiment(ticker: str, days: int = 7) -> dict:
    """
    Get recent news articles and simple sentiment for a ticker.
    """
    return {"articles": SentimentTool.get_news_sentiment(ticker, days)}

@mcp.tool()
def get_reddit_sentiment(ticker: str, limit: int = 10) -> dict:
    """
    Get recent Reddit sentiment (Mock).
    """
    return {"posts": SentimentTool.get_reddit_sentiment(ticker, limit)}

if __name__ == "__main__":
    mcp.run()
