import asyncio
import functools
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from src.utils.logging import setup_logging

logger = setup_logging(__name__)

def with_retry(max_attempts=3, min_wait=1, max_wait=10):
    """
    Decorator for adding retry logic to functions.
    Uses exponential backoff strategies.
    """
    def decorator(func):
        @functools.wraps(func)
        @retry(
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(multiplier=min_wait, max=max_wait),
            retry=retry_if_exception_type((ConnectionError, TimeoutError, IOError)),
            reraise=True
        )
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.warning(f"Retrying {func.__name__} due to error: {str(e)}")
                raise e
        return wrapper
    return decorator

def async_retry(max_attempts=3, min_wait=1, max_wait=10):
    """
    Decorator for adding retry logic to async functions.
    """
    def decorator(func):
        @functools.wraps(func)
        @retry(
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(multiplier=min_wait, max=max_wait),
            retry=retry_if_exception_type((ConnectionError, TimeoutError, IOError)),
            reraise=True
        )
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logger.warning(f"Retrying {func.__name__} due to error: {str(e)}")
                raise e
        return wrapper
    return decorator
