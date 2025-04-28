from functools import lru_cache
from typing import TypeVar
from pydantic_settings import BaseSettings, SettingsConfigDict

T = TypeVar ("T", bound="AppConfig")

class AppConfig (BaseSettings):
    """
    AppConfig (BaseSettings)

    Attributes:
        model_config (SettingsConfigDict)
    """
    model_config = SettingsConfigDict (env_file=".env", extra="allow")

    @classmethod
    @lru_cache ()
    def config (cls) -> T:
        """
        Returns:
            T
        """
        return cls ()
