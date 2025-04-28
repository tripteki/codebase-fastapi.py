from abc import ABC, abstractmethod

class Seeder (ABC):
    """
    Seeder
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
    AppSeeder
    """
    async def run (self) -> None:
        """
        Args:
            self
        Returns:
            None
        """
        pass
