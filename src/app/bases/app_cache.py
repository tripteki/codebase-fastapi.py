from typing import Optional
from fastapi import FastAPI
from fastapi_limiter import FastAPILimiter
import redis.asyncio as cache_redis
from src.app.configs.cache_config import CacheConfig

class AppCache:
    """
    AppCache

    Attributes:
        _engine (Optional[redis.asyncio.Redis])
    """
    _engine: Optional[cache_redis.Redis] = None

    @classmethod
    async def cache (cls, app: FastAPI) -> cache_redis.Redis:
        """
        Args:
            cls
            app (FastAPI)
        Returns:
            Engine
        """
        if cls._engine is None:
            cacheConfig = CacheConfig.config ()
            redisUri = cacheConfig.redis_uri ()
            cls._engine = cache_redis.from_url (redisUri, encoding="utf-8", decode_responses=True)
            await FastAPILimiter.init (cls._engine)
        return cls._engine
