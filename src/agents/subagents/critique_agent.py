from langchain_core.messages import SystemMessage, HumanMessage
from src.agents.state import ResearchState
from src.agents.prompts.critique_prompt import CRITIQUE_PROMPT
from src.llm.router import router
from src.utils.logging import setup_logging

logger = setup_logging(__name__)

async def critique_agent_node(state: ResearchState):
    """
    Agent responsible for critiquing the draft report.
    """
    ticker = state['ticker']
    draft = state.get('draft_report', "")
    
    if not draft:
        return {"critique": "No draft to critique."}
        
    logger.info(f"Critique Agent reviewing draft for {ticker}...")
    
    llm = router.get_llm()
    messages = [
        SystemMessage(content=CRITIQUE_PROMPT.format(ticker=ticker)),
        HumanMessage(content=f"Here is the draft report:\n\n{draft}")
    ]
    
    try:
        response = llm.invoke(messages)
        return {"critique": response.content}
    except Exception as e:
        logger.error(f"Critique Agent failed: {e}")
        return {"critique": f"Error: {str(e)}"}
