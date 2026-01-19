import json
from langchain_core.messages import SystemMessage, HumanMessage
from src.agents.state import ResearchState
from src.agents.prompts.fundamentals_prompt import FUNDAMENTALS_PROMPT
from src.llm.router import router
from src.utils.logging import setup_logging
from src.utils.mcp_client import call_mcp_tool
from typing import Any

logger = setup_logging(__name__)

async def fundamentals_agent_node(state: ResearchState):
    """
    Agent responsible for fundamental analysis.
    """
    ticker = state['ticker']
    logger.info(f"Fundamentals Agent starting for {ticker}...")
    
    # Paths to MCP servers
    # Assumes running from project root
    yahoo_mcp = "src/mcp_servers/yahoo_finance.py"
    fred_mcp = "src/mcp_servers/fred.py"
    
    # 1. Gather Data via MCP
    logger.info("Calling Yahoo Finance MCP...")
    info = await call_mcp_tool(yahoo_mcp, "get_stock_info", ticker=ticker)
    financials = await call_mcp_tool(yahoo_mcp, "get_financials", ticker=ticker)
    
    logger.info("Calling FRED MCP...")
    gdp = await call_mcp_tool(fred_mcp, "get_economic_data", series_id="GDP")
    unrate = await call_mcp_tool(fred_mcp, "get_economic_data", series_id="UNRATE")
    
    # 2. Prepare Context for LLM
    # Helper to safe get
    def get_val(data, key, default="N/A"):
        if isinstance(data, dict):
            return data.get(key, default)
        return default

    context = f"""
    Ticker: {ticker}
    
    Stock Info:
    {json.dumps(info, indent=2) if isinstance(info, dict) else info}
    
    Financials (Partial):
    Income: {list(financials.get('income_statement', {}).keys())[:5] if isinstance(financials, dict) and 'income_statement' in financials else "N/A"}... 
    
    Macro Data:
    GDP: {get_val(gdp, 'latest_value')} ({get_val(gdp, 'latest_date')})
    Unemployment: {get_val(unrate, 'latest_value')} ({get_val(unrate, 'latest_date')})
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
