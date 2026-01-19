from deepagents import create_deep_agent
from src.agents.prompts.main_prompt import MAIN_AGENT_PROMPT
from src.agents.prompts.fundamentals_prompt import FUNDAMENTALS_PROMPT
from src.agents.prompts.sentiment_prompt import SENTIMENT_PROMPT
from src.agents.prompts.forecast_prompt import FORECAST_PROMPT
from src.agents.prompts.critique_prompt import CRITIQUE_PROMPT
from src.llm.router import router
from src.agents.state import ResearchState

from src.agents.tools_registry import FUNDAMENTALS_TOOLS, SENTIMENT_TOOLS, FORECAST_TOOLS

def create_graph():
    """
    Create the Multi-Agent System using DeepAgents with full middleware support.
    """
    llm = router.get_llm()
    
    # Define Sub-Agents
    subagents = [
        {
            "name": "fundamentals_analyst", 
            "description": "Analyzes financial health, valuation metrics, and macro context for a stock.",
            "system_prompt": FUNDAMENTALS_PROMPT,
            "tools": FUNDAMENTALS_TOOLS
        },
        {
            "name": "sentiment_analyst",
            "description": "Analyzes market news and sentiment for a stock.",
            "system_prompt": SENTIMENT_PROMPT,
            "tools": SENTIMENT_TOOLS
        },
        {
            "name": "quantitative_analyst",
            "description": "Performs price forecasting and technical analysis for a stock.",
            "system_prompt": FORECAST_PROMPT,
            "tools": FORECAST_TOOLS
        },
        {
            "name": "critique_reviewer",
            "description": "Reviews draft reports for quality, consistency, and completeness.",
            "system_prompt": CRITIQUE_PROMPT,
            "tools": [] 
        }
    ]
    
    # Create Deep Agent with full middleware (TodoList, Filesystem, SubAgent)
    app = create_deep_agent(
        model=llm,
        tools=[],
        subagents=subagents,
        system_prompt=MAIN_AGENT_PROMPT
    )
    
    return app

app = create_graph()
