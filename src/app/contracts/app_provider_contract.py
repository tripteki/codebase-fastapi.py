from abc import ABC, abstractmethod
from typing import Any, Optional

class AppProviderContract (ABC):
    """
    AppProviderContract
    """
    @staticmethod
    @abstractmethod
    def register (app: Any) -> Optional[Any]:
        """
        Args:
            app (Any)
        Returns:
            Optional[Any]
        """
        pass

    @staticmethod
    @abstractmethod
    def boot (app: Any) -> None:
        """
        Args:
            app (Any)
        Returns:
            None
        """
        pass
