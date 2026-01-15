import json
from langchain_core.messages import SystemMessage, HumanMessage
from src.agents.state import ResearchState
from src.agents.prompts.fundamentals_prompt import FUNDAMENTALS_PROMPT
from src.llm.router import router
from src.tools.financial.yahoo_finance import YahooFinanceTool
from src.tools.financial.fred import FREDTool
from src.utils.logging import setup_logging

logger = setup_logging(__name__)

async def fundamentals_agent_node(state: ResearchState):
    """
    Agent responsible for fundamental analysis.
    """
    ticker = state['ticker']
    logger.info(f"Fundamentals Agent starting for {ticker}...")
    
    # 1. Gather Data
    yf = YahooFinanceTool()
    fred = FREDTool()
    
    info = yf.get_stock_info(ticker)
    financials = yf.get_financials(ticker)
    # earnings = yf.get_earnings(ticker) 
    
    # GDP and Unemployment as macro context
    gdp = fred.get_economic_data("GDP")
    unrate = fred.get_economic_data("UNRATE")
    
    # 2. Prepare Context for LLM
    context = f"""
    Ticker: {ticker}
    
    Stock Info:
    {json.dumps(info, indent=2)}
    
    Financials (Partial):
    Income: {list(financials.get('income_statement', {}).keys())[:5]}... use tools for full detail if needed.
    
    Macro Data:
    GDP: {gdp.get('latest_value')} ({gdp.get('latest_date')})
    Unemployment: {unrate.get('latest_value')} ({unrate.get('latest_date')})
    """
    
    # 3. Call LLM for Analysis
    llm = router.get_llm()
    messages = [
        SystemMessage(content=FUNDAMENTALS_PROMPT.format(ticker=ticker)),
        HumanMessage(content=f"Here is the gathered data:\n{context}\n\nAnalyze this and provide the JSON output.")
    ]
    
    try:
        response = llm.invoke(messages)
        content = response.content
        
        # Simple cleaning of code blocks
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].strip()
            
        analysis = json.loads(content)
        
        return {
            "fundamentals_data": {
                "raw_info": info,
                "analysis": analysis
            }
        }
    except Exception as e:
        logger.error(f"Fundamentals Agent failed: {e}")
        return {
            "fundamentals_data": {
                "error": str(e)
            }
        }
