from typing import Optional, List, Dict
from langchain_core.language_models import BaseChatModel
from src.llm.providers.groq_provider import GroqProvider
from src.llm.providers.gemini_provider import GeminiProvider
try:
    from src.llm.providers.mlx_provider import MLXProvider
    HAS_MLX = True
except ImportError:
    HAS_MLX = False
from src.llm.providers.lmstudio_provider import LMStudioProvider
from src.utils.logging import setup_logging

logger = setup_logging(__name__)

class LLMRouter:
    def __init__(self):
        self.groq = GroqProvider()
        self.gemini = GeminiProvider()
        
        if HAS_MLX:
            self.mlx = MLXProvider()
        else:
            self.mlx = None
            
        self.lmstudio = LMStudioProvider()
        
    def get_llm(self) -> BaseChatModel:
        """
        Returns the LLM provider.
        Prioritizes LM Studio (local) as requested.
        """
        # 0. Try LM Studio (http://127.0.0.1:1234)
        # Prioritize Local LM Studio if running
        llm = self.lmstudio.get_llm()
        if llm:
            logger.info("Routing request to LM Studio (local).")
            return llm

        # 1. Try Groq (Cloud - High Performance)
        llm = self.groq.get_llm()
        if llm:
            logger.info("Routing request to Groq (Cloud).")
            return llm

        # 2. Fallback to MLX (local Apple Silicon)
        if self.mlx:
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
            "mlx": self.mlx.is_available() if self.mlx else False,
            "groq": self.groq.is_available(),
            "gemini": self.gemini.is_available(),
        }

# Global Router Instance
router = LLMRouter()
