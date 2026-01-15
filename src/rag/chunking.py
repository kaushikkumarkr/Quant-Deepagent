from typing import List, Dict
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.utils.logging import setup_logging
import re

logger = setup_logging(__name__)

class ChunkingStrategy:
    """Base interface for chunking strategies."""
    def chunk(self, text: str, metadata: Dict) -> List[Dict]:
        raise NotImplementedError

class RecursiveChunker(ChunkingStrategy):
    """
    Standard recursive character text splitter.
    """
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ".", " ", ""]
        )

    def chunk(self, text: str, metadata: Dict) -> List[Dict]:
        if not text:
            return []
            
        chunks = self.splitter.create_documents([text], metadatas=[metadata])
        
        return [
            {
                "text": chunk.page_content,
                "metadata": chunk.metadata
            }
            for chunk in chunks
        ]

class SECChunker(ChunkingStrategy):
    """
    Specialized chunker for SEC filings. 
    Attempts to identify sections first, then chunks within sections.
    """
    
    def __init__(self, chunk_size: int = 2000, chunk_overlap: int = 200):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        # Regex for common 10-K headers
        self.section_patterns = {
            "RISK_FACTORS": re.compile(r"Item\s+1A[\.\:\s]+Risk\s+Factors", re.IGNORECASE),
            "MDA": re.compile(r"Item\s+7[\.\:\s]+Management.*Analysis", re.IGNORECASE),
            "BUSINESS": re.compile(r"Item\s+1[\.\:\s]+Business", re.IGNORECASE)
        }

    def chunk(self, text: str, metadata: Dict) -> List[Dict]:
        if not text:
            return []

        # Simple section logic: split by huge headers if possible, 
        # but SEC text extraction is messy. 
        # For robustness, we will just use recursive splitting but add "SEC" context
        
        chunks = self.splitter.create_documents([text], metadatas=[metadata])
        
        # Post-process: Try to detect which section a chunk belongs to 
        # (This is naive but efficient)
        final_chunks = []
        current_section = "UNKNOWN"
        
        for chunk in chunks:
            content = chunk.page_content
            
            # Check if this chunk starts a new section
            for name, pattern in self.section_patterns.items():
                if pattern.search(content[:200]): # Check start of chunk
                    current_section = name
            
            meta = chunk.metadata.copy()
            meta["section"] = current_section
            meta["char_count"] = len(content)
            
            final_chunks.append({
                "text": content,
                "metadata": meta
            })
            
        return final_chunks
