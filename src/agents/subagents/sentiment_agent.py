import json
from langchain_core.messages import SystemMessage, HumanMessage
from src.agents.state import ResearchState
from src.agents.prompts.sentiment_prompt import SENTIMENT_PROMPT
from src.llm.router import router
from src.utils.logging import setup_logging
from src.utils.mcp_client import call_mcp_tool

logger = setup_logging(__name__)

async def sentiment_agent_node(state: ResearchState):
    """
    Agent responsible for sentiment analysis.
    """
    ticker = state['ticker']
    logger.info(f"Sentiment Agent starting for {ticker}...")
    
    mcp_server = "src/mcp_servers/sentiment.py"
    
    # 1. Gather Data via MCP
    logger.info("Calling Sentiment MCP (News)...")
    news_sentiment = await call_mcp_tool(mcp_server, "get_news_sentiment", ticker=ticker, days=7)
    
    logger.info("Calling Sentiment MCP (Reddit)...")
    reddit_sentiment = await call_mcp_tool(mcp_server, "get_reddit_sentiment", ticker=ticker)
    
    # 2. Prepare Context
    context = f"""
    Ticker: {ticker}
    
    News Analysis (Last 7 Days):
    {json.dumps(news_sentiment[:5] if isinstance(news_sentiment, list) else news_sentiment, indent=2)}
    
    Reddit Sentiment:
    {json.dumps(reddit_sentiment, indent=2)}
    """
    
    # 3. Call LLM for Synthesis
    llm = router.get_llm()
    messages = [
        SystemMessage(content=SENTIMENT_PROMPT.format(ticker=ticker)),
        HumanMessage(content=f"Here is the gathered data:\n{context}\n\nAnalyze this and provide the JSON output.")
    ]
    
    try:
        response = llm.invoke(messages)
        content = response.content
        
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].strip()
            
        analysis = json.loads(content)
        
        return {
            "sentiment_data": {
                "raw_news": news_sentiment,
                "raw_reddit": reddit_sentiment,
                "analysis": analysis
            }
        }
    except Exception as e:
        logger.error(f"Sentiment Agent failed: {e}")
        return {"sentiment_data": {"error": str(e)}}
