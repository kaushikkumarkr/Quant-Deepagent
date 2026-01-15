from typing import TypedDict, List, Dict, Any, Optional, Annotated
from langchain_core.messages import BaseMessage
import operator

class ResearchState(TypedDict):
    ticker: str
    plan: List[str]
    # Data gathering results
    fundamentals_data: Dict[str, Any]
    sentiment_data: Dict[str, Any]
    forecast_data: Dict[str, Any]
    rag_data: List[Dict[str, Any]]
    
    # Reporting
    draft_report: str
    critique: str
    final_report: str
    
    # Conversation history
    messages: Annotated[List[BaseMessage], operator.add]
