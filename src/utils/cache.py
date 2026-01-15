import functools
import os
from diskcache import Cache
from src.config import settings
from src.utils.logging import setup_logging

logger = setup_logging(__name__)

# Ensure cache directory exists
CACHE_DIR = os.path.join(os.getcwd(), "data/cache")
os.makedirs(CACHE_DIR, exist_ok=True)

# Initialize DiskCache
# Size limit: 1GB, Eviction: Least Recently Used
_cache = Cache(CACHE_DIR, size_limit=int(1e9))

def disk_cache(expire=3600):
    """
    Decorator to cache function results to disk.
    :param expire: Expiration time in seconds (default 1 hour)
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create a unique key based on function name and arguments
            key = f"{func.__module__}.{func.__name__}:{str(args)}:{str(kwargs)}"
            
            if key in _cache:
                logger.debug(f"Cache hit for {func.__name__}")
                return _cache[key]
            
            try:
                result = func(*args, **kwargs)
                _cache.set(key, result, expire=expire)
                return result
            except Exception as e:
                # Don't cache failures
                raise e
        return wrapper
    return decorator

def clear_cache():
    """Clear all cached data."""
    _cache.clear()
    logger.info("Cache cleared.")
