import logging
from typing import Optional

from src.app.bases.app_event import getEventEmitter
from src.app.bases.app_i18n import AppI18n
from src.v1.api.notification.dtos.notification_validator_dto import NotificationCreateValidatorDto
from src.v1.api.notification.services.notification_user_service import NotificationUserService
from src.v1.api.user.databases.models.user_model import User
from src.v1.api.user.events.user.admin.created.event import UserAdminCreatedEvent
from src.v1.api.user.repositories.user_auth_repository import UserAuthRepository
from src.v1.api.user.repositories.user_profile_repository import UserProfileRepository

logger = logging.getLogger (__name__)

class AccountNotifier:
    """
    AccountNotifier
    """

    @staticmethod
    async def notify (recipientId: str, type: str, data: dict) -> None:
        """
        Args:
            recipientId (str)
            type (str)
            data (dict)
        Returns:
            None
        """
        try:
            recipient = await UserAuthRepository.findOneById (recipientId)
            if recipient is None or recipient.deleted_at is not None:
                return
            await NotificationUserService.notify (
                recipientId,
                NotificationCreateValidatorDto (user_id=recipientId, type=type, data=data),
            )
        except Exception:
            logger.warning (
                "notify failed type=%s recipient_id=%s",
                type,
                recipientId,
                exc_info=True,
            )

    @staticmethod
    async def _displayName (user: User) -> str:
        """
        Args:
            user (User)
        Returns:
            str
        """
        profile = await UserProfileRepository.findProfileByUserId (user.id)
        return (profile.full_name if profile and profile.full_name else None) or user.name or user.email

    @staticmethod
    async def accountCreated (user: User, role: str) -> None:
        """
        Args:
            user (User)
            role (str)
        Returns:
            None
        """
        i18n = AppI18n.i18n ()
        roleLabel = i18n.t (f"_v1_user.roles.{role}")
        await AccountNotifier.notify (user.id, "user.account.created", {
            "title": i18n.t ("_v1_user.account_created.title"),
            "body": i18n.t ("_v1_user.account_created.body", args={"role": roleLabel}),
            "url": "/admin/dashboard",
        })
        await getEventEmitter ().emit ("v1.user.admin.created", UserAdminCreatedEvent (
            id=user.id,
            name=await AccountNotifier._displayName (user),
            email=user.email,
            roleLabel=roleLabel,
        ))

    @staticmethod
    async def roleChanged (user: User, role: str) -> None:
        """
        Args:
            user (User)
            role (str)
        Returns:
            None
        """
        i18n = AppI18n.i18n ()
        await AccountNotifier.notify (user.id, "user.role.changed", {
            "title": i18n.t ("_v1_user.role_changed.title"),
            "body": i18n.t ("_v1_user.role_changed.body", args={"role": i18n.t (f"_v1_user.roles.{role}")}),
            "url": "/admin/dashboard",
        })
