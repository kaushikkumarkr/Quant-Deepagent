from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseChatModel
from src.utils.logging import setup_logging
import httpx
import os

logger = setup_logging(__name__)

class LMStudioProvider:
    def __init__(self):
        # Allow override via environment variable (for Docker)
        self.base_url = os.getenv("LM_STUDIO_URL", "http://127.0.0.1:1234/v1")
        self.api_key = "lm-studio" # LM Studio uses a dummy key
        # We can probably fetch the loaded model or just use a generic name
        self.model = "meta-llama-3.1-8b-instruct" 

    def is_available(self) -> bool:
        try:
            # Check models endpoint
            # Strip /v1 if present for the health check path construction if needed, 
            # but usually /v1/models works. 
            # httpx.get(f"{self.base_url}/models") should be http://host.docker.internal:1234/v1/models
            response = httpx.get(f"{self.base_url}/models", timeout=2.0)
            return response.status_code == 200
        except Exception as e:
            # logger.warning(f"LM Studio not detected at {self.base_url}: {e}")
            return False

    def get_llm(self) -> Optional[BaseChatModel]:
        if not self.is_available():
            # Silent fail for router fallback logic
            return None
            
        try:
            logger.info(f"Initializing LM Studio LLM at {self.base_url} with model: {self.model}")
            return ChatOpenAI(
                base_url=self.base_url,
                api_key=self.api_key,
                model=self.model,
                temperature=0,
            )
        except Exception as e:
            logger.error(f"Failed to initialize LM Studio LLM: {str(e)}")
            return None
