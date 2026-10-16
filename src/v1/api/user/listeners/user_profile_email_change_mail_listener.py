import json
import logging
from urllib.parse import parse_qs, quote, urlencode, urlparse, urlunparse
from src.app.bases.app_event import OnEvent
from src.app.bases.app_i18n import AppI18n
from src.app.bases.app_mail import AppMail
from src.app.configs.app_config import AppConfig
from src.v1.api.user.events.user.auth.registered.event import UserAuthRegisteredEvent

logger = logging.getLogger (__name__)

@OnEvent ("v1.user.profile.email-change")
async def handleUserProfileEmailChange (event: UserAuthRegisteredEvent) -> None:
    """
    Args:
        event (UserAuthRegisteredEvent)
    Returns:
        None
    """
    try:
        token = (event.token or "").strip ()
        if not token:
            logger.warning (
                "skip email change email: missing signed token email=%s",
                event.email,
            )
            return

        appConfig = AppConfig.config ()
        i18n = AppI18n.i18n ()
        subject = i18n.t ("_v1_user.account_email_change.subject")
        encodedEmail = quote (str (event.email or ""), safe="")
        baseUrl = f"{appConfig.frontend_url}/auth/verify-email/{encodedEmail}"
        parsedUrl = urlparse (baseUrl)
        queryParams = parse_qs (parsedUrl.query)
        queryParams["signed"] = [token]
        context = {
            "close_greeting": i18n.t ("_v1_user.common.close_greeting", args={"appName": appConfig.app_name}),
            "start_greeting": i18n.t ("_v1_user.common.start_greeting", args={"name": event.name}),
            "line1": i18n.t ("_v1_user.account_email_change.line1"),
            "line2": i18n.t ("_v1_user.account_email_change.line2"),
            "verify": i18n.t ("_v1_user.account_email_change.verify"),
            "title": subject,
            "user_name": event.name,
            "user_email": event.email,
            "link": urlunparse ((
                parsedUrl.scheme,
                parsedUrl.netloc,
                parsedUrl.path,
                parsedUrl.params,
                urlencode (queryParams, doseq=True),
                parsedUrl.fragment,
            )),
        }
        if appConfig.app_env != "production":
            logger.info ("=" * 70)
            logger.info ("User Email Change Email")
            logger.info ("=" * 70)
            logger.info ("To: %s", event.email)
            logger.info ("Subject: %s", subject)
            logger.info ("Template: user/auth/registered.html")
            logger.info ("Context:")
            logger.info (json.dumps (context, indent=2, ensure_ascii=False))
            logger.info ("Event Data:")
            logger.info (json.dumps ({
                "id": event.id,
                "name": event.name,
                "email": event.email,
                "email_verified_at": str (event.email_verified_at) if event.email_verified_at else None,
                "created_at": str (event.created_at) if event.created_at else None,
                "updated_at": str (event.updated_at) if event.updated_at else None,
                "token": event.token,
            }, indent=2, ensure_ascii=False))
            logger.info ("=" * 70)
            return
        sent = await AppMail.sendMail (
            to=event.email,
            subject=subject,
            template="user/auth/registered.html",
            context=context,
        )
        if not sent:
            logger.warning (
                "mail send failed to=%s template=user/auth/registered.html",
                event.email,
            )
    except Exception as e:
        logger.error (
            "Error sending email change email to %s: %s",
            event.email,
            e,
            exc_info=True,
        )
