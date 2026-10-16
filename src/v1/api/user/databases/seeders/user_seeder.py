from datetime import datetime
from src.app.bases.app_auth import AppAuth
from src.app.configs.app_config import AppConfig
from src.v1.api.user.databases.factories.user_factory import UserFactory
from src.v1.api.setting.databases.seeders.setting_seeder import SettingSeeder
from src.v1.api.user.databases.seeders.user_acl_seeder import UserAclSeeder
from src.v1.api.user.dtos.user_enum import UserEnum
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
        name = UserEnum.Superuser.value
        await UserFactory.create ({
            "name": name,
            "email": f"{name}@{AppConfig.config ().email_server ()}",
            "password": AppAuth.hashPassword ("12345678"),
            "email_verified_at": datetime.utcnow (),
        })

        for _ in range (max (count - 1, 0)):
            await UserFactory.create ()

        UserAclSeeder.run ()
        SettingSeeder.run ()
