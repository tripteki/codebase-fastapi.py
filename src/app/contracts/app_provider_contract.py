from abc import ABC, abstractmethod
from typing import Optional
from fastapi import FastAPI

class AppProviderContract (ABC):
    """
    AppProviderContract (ABC)
    """
    @staticmethod
    @abstractmethod
    def register (app: FastAPI) -> Optional[object]:
        """
        Args:
            app (FastAPI)
        Returns:
            Optional[object]
        """
        pass

    @staticmethod
    @abstractmethod
    def boot (app: FastAPI) -> None:
        """
        Args:
            app (FastAPI)
        Returns:
            None
        """
        pass
