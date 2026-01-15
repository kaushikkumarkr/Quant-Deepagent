from typing import List
from sentence_transformers import SentenceTransformer
import numpy as np
from src.utils.logging import setup_logging

logger = setup_logging(__name__)

class LocalEmbeddings:
    _instance = None
    _model_name = "all-MiniLM-L6-v2"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LocalEmbeddings, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self):
        if self.initialized:
            return
            
        logger.info(f"Loading embedding model: {self._model_name}...")
        try:
            self.model = SentenceTransformer(self._model_name)
            self.initialized = True
            logger.info("Embedding model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise e

    def embed_query(self, text: str) -> List[float]:
        """
        Embed a single query string.
        """
        if not text:
            return []
        try:
            embedding = self.model.encode(text)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error embedding query: {e}")
            return []

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Embed a list of documents.
        """
        if not texts:
            return []
        try:
            embeddings = self.model.encode(texts)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error embedding documents: {e}")
            return []
