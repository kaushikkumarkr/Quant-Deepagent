import json
from langchain_core.messages import SystemMessage, HumanMessage
from src.agents.state import ResearchState
from src.agents.prompts.forecast_prompt import FORECAST_PROMPT
from src.llm.router import router
from src.tools.forecast.prophet_forecast import ProphetTool
from src.tools.forecast.technical_indicators import TechnicalAnalysis
from src.utils.logging import setup_logging

logger = setup_logging(__name__)

async def forecast_agent_node(state: ResearchState):
    """
    Agent responsible for forecasting and technical analysis.
    """
    ticker = state['ticker']
    logger.info(f"Forecast Agent starting for {ticker}...")
    
    # 1. Gather Data
    prophet = ProphetTool()
    tech = TechnicalAnalysis()
    
    forecast = prophet.forecast_price(ticker)
    indicators = tech.calculate_indicators(ticker)
    
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
