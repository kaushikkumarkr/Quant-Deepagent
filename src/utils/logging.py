import logging
import sys
from src.config import settings

def setup_logging(name: str) -> logging.Logger:
    """
    Configure structured logging for the application.
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        level = getattr(logging, settings.log_level.upper(), logging.INFO)
        logger.setLevel(level)
        
    return logger
