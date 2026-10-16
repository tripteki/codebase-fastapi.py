from datetime import datetime
from typing import Optional
from src.app.bases.app_auth import AppAuth
from src.app.databases.factories.app_factory import AppFactory
from src.v1.api.user.databases.models.user_model import User
from src.v1.api.user.repositories.user_admin_repository import UserAdminRepository
from src.v1.api.user.repositories.user_auth_repository import UserAuthRepository

class UserFactory (AppFactory):
    """
    UserFactory (AppFactory)
    """
    @staticmethod
    def definition () -> dict:
        """
        Returns:
            dict
        """
        return {
            "name": AppFactory.faker ().name (),
            "email": AppFactory.faker ().email (),
            "password": AppAuth.hashPassword ("password123"),
            "email_verified_at": datetime.utcnow (),
            "deleted_at": None
        }

    @staticmethod
    def make (attributes: Optional[dict] = None) -> User:
        """
        Args:
            attributes (Optional[dict])
        Returns:
            User
        """
        data = UserFactory.definition ()
        if attributes:
            data.update ({
                key: value
                for key, value in attributes.items ()
                if key != "full_name"
            })
        return User (**data)

    @staticmethod
    async def create (attributes: Optional[dict] = None) -> User:
        """
        Args:
            attributes (Optional[dict])
        Returns:
            User
        """
        attrs = dict (attributes or {})
        fullNameRaw = attrs.pop ("full_name", None)
        fullName = fullNameRaw.strip () if isinstance (fullNameRaw, str) else None
        if fullName and "name" not in attrs:
            attrs["name"] = fullName
        user = UserFactory.make (attrs if attributes is not None else None)
        user = await UserAuthRepository.create (user)
        resolved = fullName or (user.name or "").strip () or user.email
        await UserAdminRepository ().upsertProfile (user.id, resolved)
        return user
