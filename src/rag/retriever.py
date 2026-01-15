from typing import List, Dict, Optional
from src.rag.vectorstore import QuantChroma
from src.utils.logging import setup_logging

logger = setup_logging(__name__)

class HybridRetriever:
    """
    Retriever that combines semantic search with metadata filtering.
    """
    
    def __init__(self):
        self.vectorstore = QuantChroma()

    def retrieve(self, query: str, ticker: str = None, limit: int = 5) -> List[Dict]:
        """
        Retrieve relevant documents for a query, optionally filtered by ticker.
        """
        where_filter = None
        if ticker:
            where_filter = {"ticker": ticker}
            
        logger.info(f"Retrieving for query: '{query}' (Ticker: {ticker})")
        
        results = self.vectorstore.query(
            query_text=query,
            n_results=limit,
            where=where_filter
        )
        
        return results

    def retrieve_context(self, query: str, ticker: str = None) -> str:
        """
        Retrieve and format results as a single context string for LLMs.
        """
        docs = self.retrieve(query, ticker=ticker, limit=5)
        
        if not docs:
            return "No relevant context found."
            
        context_parts = []
        for i, doc in enumerate(docs, 1):
            source = doc['metadata'].get('filing_type', 'Unknown Source')
            date = doc['metadata'].get('date', '')
            text = doc['text']
            context_parts.append(f"Source {i} ({source} {date}):\n{text}\n")
            
        return "\n".join(context_parts)
