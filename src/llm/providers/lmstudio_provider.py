from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseChatModel
from src.utils.logging import setup_logging
import httpx

logger = setup_logging(__name__)

class LMStudioProvider:
    def __init__(self):
        self.base_url = "http://127.0.0.1:1234/v1"
        self.api_key = "lm-studio" # LM Studio uses a dummy key
        # We can probably fetch the loaded model or just use a generic name
        self.model = "gpt-3.5-turbo" # Trick for compatibility 

    def is_available(self) -> bool:
        try:
            # Check models endpoint
            response = httpx.get(f"{self.base_url}/models", timeout=2.0)
            return response.status_code == 200
        except Exception:
            logger.warning(f"LM Studio not detected at {self.base_url}")
            return False

    def get_llm(self) -> Optional[BaseChatModel]:
        if not self.is_available():
            logger.error("LM Studio service is not running locally.")
            return None
            
        try:
            logger.info(f"Initializing LM Studio LLM with model: {self.model}")
            return ChatOpenAI(
                base_url=self.base_url,
                api_key=self.api_key,
                model=self.model,
                temperature=0,
            )
        except Exception as e:
            logger.error(f"Failed to initialize LM Studio LLM: {str(e)}")
            return None
