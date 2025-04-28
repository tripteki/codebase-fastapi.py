from typing import TypeVar, Type
from functools import lru_cache
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
    def config (cls: Type[T]) -> T:
        """
        Args:
            cls (Type[T])
        Returns:
            T
        """
        return cls ()
