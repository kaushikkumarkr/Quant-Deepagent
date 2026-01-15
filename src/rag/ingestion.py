import os
from typing import List
from src.tools.financial.sec_edgar import SECTool
from src.rag.chunking import SECChunker
from src.rag.vectorstore import QuantChroma
from src.utils.logging import setup_logging

logger = setup_logging(__name__)

class IngestionPipeline:
    """
    Pipeline to download, process, and index SEC filings.
    """
    
    def __init__(self):
        self.sec_tool = SECTool()
        self.chunker = SECChunker()
        self.vectorstore = QuantChroma()

    def ingest_ticker(self, ticker: str, limit: int = 1):
        """
        Run full ingestion for a ticker.
        """
        logger.info(f"Starting ingestion for {ticker}...")
        
        # 1. Download Filings
        files = self.sec_tool.download_filings(ticker, limit=limit)
        if not files:
            logger.warning(f"No filings found for {ticker}.")
            return

        # 2. Process Each File
        for file_path in files:
            try:
                logger.info(f"Processing {file_path}...")
                text = self.sec_tool.extract_text(file_path)
                
                if not text:
                    continue
                    
                # 3. Chunking
                # Basic metadata extraction from path/filename could be improved
                filing_type = "10-K" if "10-K" in file_path else "Unknown"
                metadata = {
                    "ticker": ticker,
                    "source": file_path,
                    "filing_type": filing_type
                }
                
                chunks = self.chunker.chunk(text, metadata)
                logger.info(f"Generated {len(chunks)} chunks.")
                
                # 4. Indexing (Store in Chroma)
                self.vectorstore.add_documents(chunks)
                
            except Exception as e:
                logger.error(f"Failed to ingest {file_path}: {e}")
                
        logger.info(f"Ingestion complete for {ticker}.")
