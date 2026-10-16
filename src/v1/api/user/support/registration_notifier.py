from typing import Optional

from src.app.bases.app_i18n import AppI18n
from src.v1.api.user.databases.models.user_model import User
from src.v1.api.user.dtos.user_role_enum import UserRoleEnum
from src.v1.api.user.repositories.user_acl_repository import UserAclRepository
from src.v1.api.user.repositories.user_profile_repository import UserProfileRepository
from src.v1.api.user.support.account_notifier import AccountNotifier

class RegistrationNotifier:
    """
    RegistrationNotifier
    """

    @staticmethod
    async def afterEmailVerified (user: User, actorId: Optional[str] = None) -> None:
        """
        Args:
            user (User)
            actorId (Optional[str])
        Returns:
            None
        """
        i18n = AppI18n.i18n ()
        profile = await UserProfileRepository.findProfileByUserId (user.id)
        fullName = profile.full_name if profile and profile.full_name else None
        role = await UserAclRepository.getUserRole (user.id)
        roleLabel = i18n.t (f"_v1_user.roles.{role}") if role else "-"

        if user.id != actorId:
            await AccountNotifier.notify (user.id, "user.registration.verified", {
                "title": i18n.t ("_v1_user.registration.verified_title"),
                "body": i18n.t ("_v1_user.registration.verified_body"),
                "url": "/admin/dashboard",
            })

        staffIds = await UserAclRepository.findUserIdsByRoleNames ([
            roleName.value for roleName in UserRoleEnum.notify ()
        ])
        body = i18n.t (
            "_v1_user.registration.new_body",
            args={
                "full_name": fullName or user.name or "-",
                "email": user.email,
                "role": roleLabel,
            },
        )
        for staffId in staffIds:
            if staffId in (user.id, actorId):
                continue
            await AccountNotifier.notify (staffId, "user.registration.new", {
                "title": i18n.t ("_v1_user.registration.new_title"),
                "body": body,
                "url": f"/admin/users/{user.id}",
                "user_id": user.id,
            })
