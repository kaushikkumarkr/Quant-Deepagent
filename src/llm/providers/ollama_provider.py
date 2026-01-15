from typing import Optional
from langchain_ollama import ChatOllama
from langchain_core.language_models import BaseChatModel
from src.config import settings
from src.utils.logging import setup_logging
import httpx

logger = setup_logging(__name__)

class OllamaProvider:
    def __init__(self):
        self.base_url = settings.ollama_base_url
        # Fallback to a standard model if specific one fails, but config has default
        self.model = settings.ollama_model 

    def is_available(self) -> bool:
        try:
            response = httpx.get(f"{self.base_url}/api/tags", timeout=2.0)
            return response.status_code == 200
        except Exception:
            logger.warning(f"Ollama not detected at {self.base_url}")
            return False

    def get_llm(self) -> Optional[BaseChatModel]:
        if not self.is_available():
            logger.error("Ollama service is not running locally.")
            return None
            
        try:
            logger.info(f"Initializing Ollama LLM with model: {self.model}")
            return ChatOllama(
                base_url=self.base_url,
                model=self.model,
                temperature=0,
                # Keep alive for performance
                keep_alive="5m"
            )
        except Exception as e:
            logger.error(f"Failed to initialize Ollama LLM: {str(e)}")
            return None
