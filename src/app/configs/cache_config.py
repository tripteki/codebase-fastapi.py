from src.app.bases.app_config import AppConfig

class CacheConfig (AppConfig):
    """
    CacheConfig (AppConfig)

    Attributes:
        redis_uri (str)
    """
    redis_uri: str = ""
