from src.app.bases.app_config import AppConfig

class CacheConfig (AppConfig):
    """
    CacheConfig (AppConfig)

    Attributes:
        redis_url (str)
    """
    redis_url: str = ""
