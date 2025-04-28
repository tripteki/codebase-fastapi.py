import asyncio
import click
import redis.asyncio as cache_redis
import sys
import traceback
from src.app.bases.app_console import Command
from src.app.configs.cache_config import CacheConfig

@Command (name="cache:clear", help="Clear cache")
def cacheClearCommand () -> None:
    """
    Returns:
        None
    """
    try:
        async def clearCache () -> None:
            cacheConfig = CacheConfig.config ()
            redisUri = cacheConfig.redis_uri ()
            redisClient = cache_redis.from_url (redisUri, encoding="utf-8", decode_responses=True)
            await redisClient.flushdb ()
            await redisClient.close ()
        asyncio.run (clearCache ())
        click.echo (click.style ("Cache cleared successfully!", fg="green"))
    except Exception as e:
        traceback.print_exc ()
        click.echo (click.style (f"Error clearing cache: {str (e)}", fg="red"))
        sys.exit (1)
