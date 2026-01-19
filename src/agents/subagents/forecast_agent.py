import json
from langchain_core.messages import SystemMessage, HumanMessage
from src.agents.state import ResearchState
from src.agents.prompts.forecast_prompt import FORECAST_PROMPT
from src.llm.router import router
from src.utils.logging import setup_logging
from src.utils.mcp_client import call_mcp_tool

logger = setup_logging(__name__)

async def forecast_agent_node(state: ResearchState):
    """
    Agent responsible for forecasting and technical analysis.
    """
    ticker = state['ticker']
    logger.info(f"Forecast Agent starting for {ticker}...")
    
    mcp_server = "src/mcp_servers/forecast.py"
    
    # 1. Gather Data via MCP
    logger.info("Calling Forecast MCP (Prophet)...")
    forecast = await call_mcp_tool(mcp_server, "forecast_price", ticker=ticker)
    
    logger.info("Calling Forecast MCP (Technical Indicators)...")
    indicators = await call_mcp_tool(mcp_server, "get_technical_indicators", ticker=ticker)
    
    # 2. Prepare Context
    context = f"""
    Ticker: {ticker}
    
    Prophet Forecast:
    {json.dumps(forecast, indent=2)}
    
    Technical Indicators:
    {json.dumps(indicators, indent=2)}
    """
    
    # 3. Call LLM for Interpretation
    llm = router.get_llm()
    messages = [
        SystemMessage(content=FORECAST_PROMPT.format(ticker=ticker)),
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
            "forecast_data": {
                "raw_forecast": forecast,
                "raw_indicators": indicators,
                "analysis": analysis
            }
        }
    except Exception as e:
        logger.error(f"Forecast Agent failed: {e}")
        return {"forecast_data": {"error": str(e)}}
