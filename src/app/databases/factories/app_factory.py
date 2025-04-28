from abc import ABC, abstractmethod
from typing import Protocol, TypeVar, Optional
from faker import Faker

T = TypeVar ("T")

class Factory (Protocol[T]):
    """
    Factory (Protocol)
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
    AppFactory (ABC)

    Attributes:
        _faker (Optional[Faker])
    """
    _faker: Optional[Faker] = None

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
    def definition (self) -> object:
        """
        Args:
            self
        Returns:
            object
        """
        pass
