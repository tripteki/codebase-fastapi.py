import json
import logging
from src.app.bases.app_event import OnEvent
from src.app.bases.app_i18n import AppI18n
from src.app.bases.app_mail import AppMail
from src.app.configs.app_config import AppConfig
from src.v1.api.user.events.user.security.notice.event import UserSecurityNoticeEvent

logger = logging.getLogger (__name__)

@OnEvent ("v1.user.security.notice")
async def handleUserSecurityNotice (event: UserSecurityNoticeEvent) -> None:
    """
    Args:
        event (UserSecurityNoticeEvent)
    Returns:
        None
    """
    try:
        appConfig = AppConfig.config ()
        i18n = AppI18n.i18n ()
        context = {
            "close_greeting": i18n.t ("_v1_user.common.close_greeting", args={"appName": appConfig.app_name}),
            "start_greeting": i18n.t ("_v1_user.common.start_greeting", args={"name": event.name}),
            "title": event.subject,
            "line1": event.line1,
            "line2": event.line2,
            "link": event.link,
            "link_label": event.linkLabel,
        }
        if appConfig.app_env != "production":
            logger.info ("=" * 70)
            logger.info ("User Security Notice Email")
            logger.info ("=" * 70)
            logger.info ("To: %s", event.to)
            logger.info ("Subject: %s", event.subject)
            logger.info ("Template: user/auth/notice.html")
            logger.info ("Context:")
            logger.info (json.dumps (context, indent=2, ensure_ascii=False))
            logger.info ("=" * 70)
            return
        sent = await AppMail.sendMail (
            to=event.to,
            subject=event.subject,
            template="user/auth/notice.html",
            context=context,
        )
        if not sent:
            logger.warning (
                "mail send failed to=%s template=user/auth/notice.html",
                event.to,
            )
    except Exception as e:
        logger.error (
            "Error sending security notice email to %s: %s",
            event.to,
            e,
            exc_info=True,
        )
