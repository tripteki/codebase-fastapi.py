from datetime import datetime
from src.app.bases.app_auth import AppAuth
from src.v1.api.user.databases.factories.user_factory import UserFactory
from src.v1.api.user.databases.seeders.user_acl_seeder import UserAclSeeder
from src.app.databases.seeders.app_seeder import AppSeeder

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
        await UserFactory.create ({
            "name": "superuser",
            "email": "superuser@mail.com",
            "password": AppAuth.hashPassword ("12345678"),
            "email_verified_at": datetime.utcnow (),
        })

        for _ in range (max (count - 1, 0)):
            await UserFactory.create ()

        UserAclSeeder.run ()
