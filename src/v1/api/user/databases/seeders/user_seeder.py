from src.app.databases.seeders.app_seeder import AppSeeder
from src.v1.api.user.databases.factories.user_factory import UserFactory
from src.v1.api.user.repositories.user_auth_repository import UserAuthRepository

class UserSeeder (AppSeeder):
    """
    UserSeeder (AppSeeder)
    """
    @staticmethod
    async def run (count: int = 1) -> None:
        """
        Args:
            count (int)
        Returns:
            None
        """
        for i in range (count):
            await UserFactory.create ()
