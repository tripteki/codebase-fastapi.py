import json
import logging
from src.app.bases.app_event import OnEvent
from src.app.bases.app_i18n import AppI18n
from src.app.bases.app_mail import AppMail
from src.app.configs.app_config import AppConfig
from src.v1.api.user.events.user.admin.activated.event import UserAdminActivatedEvent

@OnEvent ("v1.user.admin.activated")
async def handleUserAdminActivated (event: UserAdminActivatedEvent) -> None:
    """
    Args:
        event (UserAdminActivatedEvent)
    Returns:
        None
    """
    try:
        appConfig = AppConfig.config ()
        i18n = AppI18n.i18n ()
        subject = i18n.t ("_v1_user.account_activated.subject")
        context = {
            "close_greeting": i18n.t ("_v1_user.common.close_greeting", args={"appName": appConfig.app_name}),
            "start_greeting": i18n.t ("_v1_user.common.start_greeting", args={"name": event.name}),
            "line": i18n.t ("_v1_user.account_activated.line"),
            "thank_you": i18n.t ("_v1_user.account_activated.thank_you"),
        }
        if appConfig.app_env != "production":
            logger = logging.getLogger (__name__)
            logger.info ("=" * 70)
            logger.info (f"User Activated Email")
            logger.info ("=" * 70)
            logger.info (f"To: {event.email}")
            logger.info (f"Subject: {subject}")
            logger.info (f"Template: user/auth/account.html")
            logger.info (f"Context:")
            logger.info (json.dumps (context, indent=2, ensure_ascii=False))
            logger.info (f"Event Data:")
            logger.info (json.dumps ({
                "id": event.id,
                "name": event.name,
                "email": event.email,
                "email_verified_at": str (event.email_verified_at) if event.email_verified_at else None,
                "created_at": str (event.created_at) if event.created_at else None,
                "updated_at": str (event.updated_at) if event.updated_at else None
            }, indent=2, ensure_ascii=False))
            logger.info ("=" * 70)
            return
        await AppMail.sendMail (
            to=event.email,
            subject=subject,
            template="user/auth/account.html",
            context=context
        )
    except Exception as e:
        logger = logging.getLogger (__name__)
        logger.error (f"Error sending user activated email to {event.email}: {e}", exc_info=True)
