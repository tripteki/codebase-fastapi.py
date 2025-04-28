from abc import ABC, abstractmethod
from typing import Protocol, TypeVar, Any
from faker import Faker

T = TypeVar ("T")

class Factory (Protocol[T]):
    """
    Factory
    """
    def definition (self) -> T:
        """
        Args:
            self
        Returns:
            T
        """
        ...

class AppFactory (ABC):
    """
    AppFactory
    """
    _faker: Any = None

    @classmethod
    def faker (cls) -> Faker:
        """
        Args:
            cls
        Returns:
            Faker
        """
        if cls._faker is None:
            cls._faker = Faker ()
        return cls._faker

    @abstractmethod
    def definition (self) -> Any:
        """
        Args:
            self
        Returns:
            Any
        """
        pass
