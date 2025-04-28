from src.app.bases.app_config import AppConfig

class CacheConfig (AppConfig):
    """
    CacheConfig (AppConfig)

    Attributes:
        memory_redis_host (str)
        memory_redis_port (int)
        memory_redis_username (str)
        memory_redis_password (str)
        memory_redis_database (int)
    """
    memory_redis_host: str = ""
    memory_redis_port: int = 0
    memory_redis_username: str = ""
    memory_redis_password: str = ""
    memory_redis_database: int = 0

    def redis_uri (self) -> str:
        """
        Args:
            self
        Returns:
            str
        """
        if not self.memory_redis_host:
            raise ValueError ("MEMORY_REDIS_HOST is required")
        if not self.memory_redis_port:
            raise ValueError ("MEMORY_REDIS_PORT is required")
        if self.memory_redis_username and self.memory_redis_password:
            return f"redis://{self.memory_redis_username}:{self.memory_redis_password}@{self.memory_redis_host}:{self.memory_redis_port}/{self.memory_redis_database}"
        elif self.memory_redis_password:
            return f"redis://:{self.memory_redis_password}@{self.memory_redis_host}:{self.memory_redis_port}/{self.memory_redis_database}"
        else:
            return f"redis://{self.memory_redis_host}:{self.memory_redis_port}/{self.memory_redis_database}"
