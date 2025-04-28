import redis.asyncio as cache_redis
from typing import Any
from fastapi_limiter import FastAPILimiter
from src.app.configs.cache_config import CacheConfig

class AppCache:
    """
    AppCache
    """
    @classmethod
    async def cache (cls, app) -> Any:
        """
        Args:
            cls
            app (FastAPI)
        Returns:
            Engine
        """
        if cls._engine is None:
            cacheConfig = CacheConfig.config ()
            cls._engine = cache_redis.from_url (cacheConfig.redis_uri, encoding="utf-8", decode_responses=True)
            await FastAPILimiter.init (cls._engine)
        return cls._engine

    """
    Attributes:
        _engine (None)
    """
    _engine = None
