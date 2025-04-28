from abc import ABC, abstractmethod

class Seeder (ABC):
    """
    Seeder (ABC)
    """
    @abstractmethod
    async def run (self) -> None:
        """
        Args:
            self
        Returns:
            None
        """
        pass

class AppSeeder (Seeder):
    """
    AppSeeder (Seeder)
    """
    async def run (self) -> None:
        """
        Args:
            self
        Returns:
            None
        """
        pass
