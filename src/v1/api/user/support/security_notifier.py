import logging
from datetime import datetime
from typing import Optional

from src.app.bases.app_event import getEventEmitter
from src.app.bases.app_i18n import AppI18n
from src.app.configs.app_config import AppConfig
from src.app.helpers.datetime_helper import formatAppDatetime
from src.v1.api.user.databases.models.user_model import User
from src.v1.api.user.events.user.security.notice.event import UserSecurityNoticeEvent
from src.v1.api.user.repositories.user_profile_repository import UserProfileRepository

logger = logging.getLogger (__name__)

class SecurityNotifier:
    """
    SecurityNotifier
    """

    @staticmethod
    def maskEmail (email: str) -> str:
        """
        Args:
            email (str)
        Returns:
            str
        """
        local, _, domain = (email or "").partition ("@")
        visible = local[:2] if len (local) > 2 else local[:1]
        return f"{visible}***@{domain}" if domain else f"{visible}***"

    @staticmethod
    async def _displayName (userId: str, fallback: str) -> str:
        """
        Args:
            userId (str)
            fallback (str)
        Returns:
            str
        """
        profile = await UserProfileRepository.findProfileByUserId (userId)
        return profile.full_name if profile and profile.full_name else fallback

    @staticmethod
    async def _send (event: UserSecurityNoticeEvent) -> None:
        """
        Args:
            event (UserSecurityNoticeEvent)
        Returns:
            None
        """
        try:
            await getEventEmitter ().emit ("v1.user.security.notice", event)
        except Exception:
            logger.warning ("security notice failed to=%s", event.to, exc_info=True)

    @staticmethod
    async def passwordChanged (user: User, actorId: Optional[str] = None) -> None:
        """
        Args:
            user (User)
            actorId (Optional[str])
        Returns:
            None
        """
        if user.deleted_at is not None:
            return
        i18n = AppI18n.i18n ()
        time = formatAppDatetime (datetime.utcnow ())
        if actorId and actorId != user.id:
            adminName = await SecurityNotifier._displayName (actorId, "-")
            line1 = i18n.t ("_v1_user.security.password_line_admin", args={"admin": adminName, "time": time})
        else:
            line1 = i18n.t ("_v1_user.security.password_line_self", args={"time": time})
        await SecurityNotifier._send (UserSecurityNoticeEvent (
            to=user.email,
            name=await SecurityNotifier._displayName (user.id, user.email),
            subject=i18n.t ("_v1_user.security.password_subject"),
            line1=line1,
            line2=i18n.t ("_v1_user.security.password_warning"),
            link=f"{AppConfig.config ().frontend_url}/login",
            linkLabel=i18n.t ("_v1_user.security.login"),
        ))

    @staticmethod
    async def emailChanged (user: User, oldEmail: str, byAdmin: bool) -> None:
        """
        Args:
            user (User)
            oldEmail (str)
            byAdmin (bool)
        Returns:
            None
        """
        if user.deleted_at is not None or not oldEmail or oldEmail.lower () == user.email.lower ():
            return
        i18n = AppI18n.i18n ()
        name = await SecurityNotifier._displayName (user.id, user.email)
        await SecurityNotifier._send (UserSecurityNoticeEvent (
            to=oldEmail,
            name=name,
            subject=i18n.t ("_v1_user.security.email_old_subject"),
            line1=i18n.t ("_v1_user.security.email_old_line", args={"email": SecurityNotifier.maskEmail (user.email)}),
            line2=i18n.t ("_v1_user.security.email_old_warning"),
        ))
        if byAdmin:
            await SecurityNotifier._send (UserSecurityNoticeEvent (
                to=user.email,
                name=name,
                subject=i18n.t ("_v1_user.security.email_new_subject"),
                line1=i18n.t ("_v1_user.security.email_new_line"),
                link=f"{AppConfig.config ().frontend_url}/login",
                linkLabel=i18n.t ("_v1_user.security.login"),
            ))
