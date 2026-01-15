import json
from langchain_core.messages import SystemMessage, HumanMessage
from src.agents.state import ResearchState
from src.agents.prompts.sentiment_prompt import SENTIMENT_PROMPT
from src.llm.router import router
from src.tools.sentiment.news_api import NewsAPITool
from src.utils.logging import setup_logging

logger = setup_logging(__name__)

async def sentiment_agent_node(state: ResearchState):
    """
    Agent responsible for sentiment analysis.
    """
    ticker = state['ticker']
    logger.info(f"Sentiment Agent starting for {ticker}...")
    
    # 1. Gather Data
    news_tool = NewsAPITool()
    
    news_sentiment = news_tool.get_news(ticker)
    
    # 2. Prepare Context
    context = f"""
    Ticker: {ticker}
    
    News Analysis (Last 7 Days):
    {json.dumps(news_sentiment[:5], indent=2)}
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
