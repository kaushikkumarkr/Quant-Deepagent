from typing import Optional
from langchain_groq import ChatGroq
from langchain_core.language_models import BaseChatModel
from src.config import settings
from src.utils.logging import setup_logging

logger = setup_logging(__name__)

class GroqProvider:
    def __init__(self):
        self.api_key = settings.groq_api_key
        self.model_name = "meta-llama/llama-4-scout-17b-16e-instruct" 

    def is_available(self) -> bool:
        if not self.api_key:
            return False
        try:
            # Simple check to see if we can instantiate
            return True
        except Exception:
            return False

    def get_llm(self) -> Optional[BaseChatModel]:
        if not self.is_available():
            logger.warning("Groq API Key not found or provider unavailable.")
            return None
            
        try:
            logger.info(f"Initializing Groq LLM with model: {self.model_name}")
            return ChatGroq(
                groq_api_key=self.api_key,
                model_name=self.model_name,
                temperature=0,
                max_retries=2
            )
        except Exception as e:
            logger.error(f"Failed to initialize Groq LLM: {str(e)}")
            return None
