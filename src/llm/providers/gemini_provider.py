from typing import Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.language_models import BaseChatModel
from src.config import settings
from src.utils.logging import setup_logging

logger = setup_logging(__name__)

class GeminiProvider:
    def __init__(self):
        self.api_key = settings.google_api_key
        self.model_name = "gemini-2.0-flash"

    def is_available(self) -> bool:
        if not self.api_key:
            return False
        return True

    def get_llm(self) -> Optional[BaseChatModel]:
        if not self.is_available():
            logger.warning("Google API Key not found or provider unavailable.")
            return None
            
        try:
            logger.info(f"Initializing Gemini LLM with model: {self.model_name}")
            return ChatGoogleGenerativeAI(
                google_api_key=self.api_key,
                model=self.model_name,
                temperature=0,
                max_retries=2,
                convert_system_message_to_human=True
            )
        except Exception as e:
            logger.error(f"Failed to initialize Gemini LLM: {str(e)}")
            return None
