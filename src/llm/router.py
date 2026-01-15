from typing import Optional, List, Dict
from langchain_core.language_models import BaseChatModel
from src.llm.providers.groq_provider import GroqProvider
from src.llm.providers.gemini_provider import GeminiProvider
from src.llm.providers.mlx_provider import MLXProvider
from src.utils.logging import setup_logging

logger = setup_logging(__name__)

class LLMRouter:
    def __init__(self):
        self.groq = GroqProvider()
        self.gemini = GeminiProvider()
        self.mlx = MLXProvider()
        
    def get_llm(self) -> BaseChatModel:
        """
        Returns the MLX local LLM for DeepAgents.
        Using local model for reliable tool calling and offline operation.
        """
        # Use MLX only (local on Apple Silicon)
        llm = self.mlx.get_llm()
        if llm:
            logger.info("Routing request to MLX (local).")
            return llm
            
        # Critical Failure
        logger.critical("MLX provider not available! Please check your configuration.")
        raise RuntimeError("MLX provider not available.")

    def check_health(self) -> Dict[str, bool]:
        """
        Returns the availability status of all providers.
        """
        return {
            "groq": self.groq.is_available(),
            "gemini": self.gemini.is_available(),
            "mlx": self.mlx.is_available()
        }

# Global Router Instance
router = LLMRouter()
