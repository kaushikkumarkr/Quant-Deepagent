from langchain_core.messages import SystemMessage, HumanMessage
from src.agents.state import ResearchState
from src.agents.prompts.main_prompt import MAIN_AGENT_PROMPT
from src.llm.router import router
from src.utils.logging import setup_logging

logger = setup_logging(__name__)

async def plan_node(state: ResearchState):
    """
    Generate initial plan.
    """
    ticker = state['ticker']
    logger.info(f"Coordinator planning research for {ticker}...")
    
    # Simple fixed plan for now as we have a fixed graph structure.
    # In a more dynamic agent, this would output the steps.
    return {
        "plan": [
            "Gather Fundamentals",
            "Analyze Sentiment",
            "Forecast Price",
            "Synthesize Report",
            "Critique & Refine"
        ]
    }

async def write_report_node(state: ResearchState):
    """
    Synthesize all data into a draft report.
    """
    ticker = state['ticker']
    logger.info(f"Coordinator writing draft report for {ticker}...")
    
    # helper to safely get data
    def get_summary(key, subkey):
        data = state.get(key, {})
        if "error" in data:
            return f"Error: {data['error']}"
        return str(data.get(subkey, "No analysis provided."))

    fund_summary = get_summary("fundamentals_data", "analysis")
    sent_summary = get_summary("sentiment_data", "analysis")
    fcst_summary = get_summary("forecast_data", "analysis")
    
    context = f"""
    1. Fundamental Analysis:
    {fund_summary}
    
    2. Sentiment Analysis:
    {sent_summary}
    
    3. Technical Forecast:
    {fcst_summary}
    """
    
    llm = router.get_llm()
    messages = [
        SystemMessage(content=MAIN_AGENT_PROMPT.format(ticker=ticker)),
        HumanMessage(content=f"Here are the findings from your team:\n{context}\n\nWrite the detailed draft report now.")
    ]
    
    try:
        response = llm.invoke(messages)
        return {"draft_report": response.content}
    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        return {"draft_report": f"Error generating report: {e}"}

async def refine_report_node(state: ResearchState):
    """
    Refine the report based on critique.
    """
    ticker = state['ticker']
    draft = state.get('draft_report')
    critique = state.get('critique')
    
    if not critique or "No major issues" in critique:
        logger.info("Critique passed, finalizing report.")
        return {"final_report": draft}
        
    logger.info(f"Coordinator refining report for {ticker}...")
    
    llm = router.get_llm()
    messages = [
        SystemMessage(content=MAIN_AGENT_PROMPT.format(ticker=ticker)),
        HumanMessage(content=f"Original Draft:\n{draft}\n\nCritique:\n{critique}\n\nPlease rewrite the report to address the critique and produce the Final Report.")
    ]
    
    try:
        response = llm.invoke(messages)
        return {"final_report": response.content}
    except Exception as e:
        logger.error(f"Refinement failed: {e}")
        return {"final_report": draft} # Fallback to draft
