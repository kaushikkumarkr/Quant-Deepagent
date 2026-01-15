import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any
import os
from src.rag.embeddings import LocalEmbeddings
from src.utils.logging import setup_logging

logger = setup_logging(__name__)

class QuantChroma:
    """
    Wrapper for ChromaDB vector store.
    """
    
    def __init__(self, collection_name: str = "sec_filings"):
        self.persist_directory = os.path.join(os.getcwd(), "data/chroma_db")
        self.client = chromadb.PersistentClient(path=self.persist_directory)
        self.embedder = LocalEmbeddings()
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def add_documents(self, chunks: List[Dict]):
        """
        Add document chunks to the vector store.
        chunks: List of dicts with 'text' and 'metadata'.
        """
        if not chunks:
            return

        texts = [c['text'] for c in chunks]
        metadatas = [c['metadata'] for c in chunks]
        
        # Generate IDs
        ids = [f"{m.get('ticker', 'UNK')}_{i}_{hash(t)}" for i, (t, m) in enumerate(zip(texts, metadatas))]
        
        # Generate embeddings
        logger.info(f"Generating embeddings for {len(texts)} chunks...")
        embeddings = self.embedder.embed_documents(texts)
        
        logger.info(f"Adding {len(texts)} documents to ChromaDB...")
        self.collection.upsert(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas
        )

    def query(self, query_text: str, n_results: int = 5, where: Dict = None) -> List[Dict]:
        """
        Semantic search.
        """
        query_embedding = self.embedder.embed_query(query_text)
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where
        )
        
        # Flatten results
        # Chroma returns lists of lists
        output = []
        if results['ids']:
            for i in range(len(results['ids'][0])):
                output.append({
                    "id": results['ids'][0][i],
                    "text": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "distance": results['distances'][0][i] if results['distances'] else 0.0
                })
                
        return output
