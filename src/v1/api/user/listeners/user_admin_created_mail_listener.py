import json
import logging
from src.app.bases.app_event import OnEvent
from src.app.bases.app_i18n import AppI18n
from src.app.bases.app_mail import AppMail
from src.app.configs.app_config import AppConfig
from src.v1.api.user.events.user.admin.created.event import UserAdminCreatedEvent

logger = logging.getLogger (__name__)

@OnEvent ("v1.user.admin.created")
async def handleUserAdminCreated (event: UserAdminCreatedEvent) -> None:
    """
    Args:
        event (UserAdminCreatedEvent)
    Returns:
        None
    """
    try:
        appConfig = AppConfig.config ()
        i18n = AppI18n.i18n ()
        subject = i18n.t ("_v1_user.account_created.subject")
        context = {
            "close_greeting": i18n.t ("_v1_user.common.close_greeting", args={"appName": appConfig.app_name}),
            "start_greeting": i18n.t ("_v1_user.common.start_greeting", args={"name": event.name}),
            "line1": i18n.t ("_v1_user.account_created.line1", args={"role": event.roleLabel}),
            "line2": i18n.t ("_v1_user.account_created.line2"),
            "login": i18n.t ("_v1_user.account_created.login"),
            "forgot": i18n.t ("_v1_user.account_created.forgot"),
            "title": subject,
            "user_name": event.name,
            "user_email": event.email,
            "login_link": f"{appConfig.frontend_url}/login",
            "forgot_link": f"{appConfig.frontend_url}/forgot-password",
        }
        if appConfig.app_env != "production":
            logger.info ("=" * 70)
            logger.info ("User Created By Admin Email")
            logger.info ("=" * 70)
            logger.info ("To: %s", event.email)
            logger.info ("Subject: %s", subject)
            logger.info ("Template: user/auth/created.html")
            logger.info ("Context:")
            logger.info (json.dumps (context, indent=2, ensure_ascii=False))
            logger.info ("=" * 70)
            return
        sent = await AppMail.sendMail (
            to=event.email,
            subject=subject,
            template="user/auth/created.html",
            context=context,
        )
        if not sent:
            logger.warning (
                "mail send failed to=%s template=user/auth/created.html",
                event.email,
            )
    except Exception as e:
        logger.error (
            "Error sending user created email to %s: %s",
            event.email,
            e,
            exc_info=True,
        )
