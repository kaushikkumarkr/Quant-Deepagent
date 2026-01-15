import os
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    # App Settings
    app_name: str = "QuantMind"
    environment: str = "development"
    log_level: str = "INFO"
    
    # LLM Providers
    groq_api_key: Optional[str] = None
    google_api_key: Optional[str] = Field(None, alias="GEMINI_API_KEY")
    
    # MLX (Local)
    mlx_model: str = "mlx-community/Llama-3.1-8B-Instruct-4bit"
    
    # Financial Data
    fred_api_key: Optional[str] = None
    fmp_api_key: Optional[str] = Field(None, alias="FINANCIAL_MODELING_PREP_API_KEY")
    news_api_key: Optional[str] = Field(None, alias="NEWS_API_KEY")
    
    # Reddit
    reddit_client_id: Optional[str] = None
    reddit_client_secret: Optional[str] = None
    reddit_user_agent: str = "QuantMind/1.0"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Global settings instance
settings = Settings()
