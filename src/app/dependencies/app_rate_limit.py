from fastapi import Depends
from fastapi_limiter.depends import RateLimiter
from src.app.configs.app_config import AppConfig

async def _rateLimitNoop () -> None:
    """
    No-op rate limit dependency for non-production environments.
    """
    return None

def rateLimit (*, times: int, seconds: int = 60):
    """
    Args:
        times (int)
        seconds (int)
    Returns:
        Depends
    """
    if AppConfig.config ().app_env != "production":
        return Depends (_rateLimitNoop)

    return Depends (RateLimiter (times=times, seconds=seconds))
