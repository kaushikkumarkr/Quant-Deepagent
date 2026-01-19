from typing import Optional, List, Dict
from langchain_core.language_models import BaseChatModel
from src.llm.providers.groq_provider import GroqProvider
from src.llm.providers.gemini_provider import GeminiProvider
from src.llm.providers.mlx_provider import MLXProvider
from src.llm.providers.lmstudio_provider import LMStudioProvider
from src.utils.logging import setup_logging

logger = setup_logging(__name__)

class LLMRouter:
    def __init__(self):
        self.groq = GroqProvider()
        self.gemini = GeminiProvider()
        self.mlx = MLXProvider()
        self.lmstudio = LMStudioProvider()
        
    def get_llm(self) -> BaseChatModel:
        """
        Returns the LLM provider.
        Prioritizes LM Studio (local) as requested.
        """
        # 1. Try LM Studio (http://127.0.0.1:1234)
        llm = self.lmstudio.get_llm()
        if llm:
            logger.info("Routing request to LM Studio (local).")
            return llm

        # 2. Fallback to MLX (local Apple Silicon)
        llm = self.mlx.get_llm()
        if llm:
            logger.info("Routing request to MLX (local).")
            return llm
            
        # Critical Failure
        logger.critical("No local LLM provider available! Please check your configuration.")
        raise RuntimeError("No local LLM provider available.")

    def check_health(self) -> Dict[str, bool]:
        """
        Returns the availability status of all providers.
        """
        return {
            "lmstudio": self.lmstudio.is_available(),
            "mlx": self.mlx.is_available(),
            "groq": self.groq.is_available(),
            "gemini": self.gemini.is_available(),
        }

# Global Router Instance
router = LLMRouter()
