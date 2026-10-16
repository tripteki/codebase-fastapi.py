from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict
import re
import aiosmtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Environment, FileSystemLoader, Template
import logging
from src.app.bases.app_view import AppView
from src.app.configs.app_config import AppConfig
from src.app.configs.mail_config import MailConfig

class AppMail:
    """
    AppMail

    Attributes:
        _smtp (Optional[aiosmtplib.SMTP])
        _config (Optional[MailConfig])
        _jinja_env (Optional[Environment])
    """
    _smtp: Optional[aiosmtplib.SMTP] = None
    _config: Optional[MailConfig] = None
    _jinja_env: Optional[Environment] = None

    @classmethod
    def config (cls) -> MailConfig:
        """
        Args:
            cls
        Returns:
            MailConfig
        """
        if cls._config is None:
            cls._config = MailConfig.config ()
        return cls._config

    @classmethod
    def smtp (cls) -> aiosmtplib.SMTP:
        """
        Args:
            cls
        Returns:
            aiosmtplib.SMTP
        """
        config = cls.config ()
        return aiosmtplib.SMTP (
            hostname=config.host,
            port=config.port,
            use_tls=config.secure,
            start_tls=config.tls,
        )

    @classmethod
    def jinjaEnv (cls) -> Environment:
        """
        Args:
            cls
        Returns:
            Environment
        """
        if cls._jinja_env is None:
            viewPath = AppView.viewPath ()
            if viewPath:
                cls._jinja_env = Environment (loader=FileSystemLoader (str (viewPath)))
            else:
                cls._jinja_env = Environment (loader=FileSystemLoader ("."))
        return cls._jinja_env

    @classmethod
    async def mailBrandName (cls) -> str:
        """
        Args:
            cls
        Returns:
            str
        """
        try:
            from src.v1.api.setting.repositories.setting_repository import SettingRepository
            setting = await SettingRepository ().findByKey ("APP_NAME")
        except Exception:
            return ""
        return (setting.value or "").strip () if setting else ""

    @classmethod
    async def mailPrimaryColor (cls) -> str:
        """
        Args:
            cls
        Returns:
            str
        """
        fallback = "#2563eb"
        try:
            from src.v1.api.setting.repositories.setting_repository import SettingRepository
            setting = await SettingRepository ().findByKey ("COLOR_PRIMARY")
        except Exception:
            return fallback
        raw = (setting.value or "").strip () if setting else ""
        if not raw:
            return fallback
        color = raw if raw.startswith ("#") else f"#{raw}"
        if re.fullmatch (r"#[0-9a-fA-F]{3}", color):
            color = "#" + "".join (ch * 2 for ch in color[1:])
        if not re.fullmatch (r"#[0-9a-fA-F]{6}", color):
            return fallback
        return color.lower ()

    @classmethod
    def primaryRgb (cls, color: str) -> str:
        """
        Args:
            color (str)
        Returns:
            str
        """
        raw = (color or "").strip ().lstrip ("#")
        if len (raw) == 3:
            raw = "".join (ch * 2 for ch in raw)
        if len (raw) != 6:
            return "37,99,235"
        try:
            return f"{int (raw[0:2], 16)},{int (raw[2:4], 16)},{int (raw[4:6], 16)}"
        except ValueError:
            return "37,99,235"

    @classmethod
    async def sendMail (
        cls,
        to: str | List[str],
        subject: str,
        body: Optional[str] = None,
        html: Optional[str] = None,
        template: Optional[str] = None,
        context: Optional[Dict[str, object]] = None,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
        attachments: Optional[List[Dict[str, object]]] = None
    ) -> bool:
        """
        Args:
            to (str | List[str])
            subject (str)
            body (Optional[str])
            html (Optional[str])
            template (Optional[str])
            context (Optional[Dict[str, object]])
            from_email (Optional[str])
            from_name (Optional[str])
            attachments (Optional[List[Dict[str, object]]])
        Returns:
            bool
        """
        config = cls.config ()
        logger = logging.getLogger (__name__)
        if not config.isConfigured ():
            logger.warning (
                "mail not configured; skip send to=%s subject=%s",
                to,
                subject,
            )
            return False

        smtp = cls.smtp ()
        context = dict (context or {})
        appConfig = AppConfig.config ()
        context.setdefault ("app_name", appConfig.app_name)
        frontendUrl = (appConfig.frontend_url or "").rstrip ("/")
        if frontendUrl:
            context.setdefault ("logo_url", f"{frontendUrl}/manifest/asset/logo.png")
        primaryColor = await cls.mailPrimaryColor ()
        context.setdefault ("primary_color", primaryColor)
        context.setdefault ("primary_rgb", cls.primaryRgb (str (context.get ("primary_color") or primaryColor)))
        context.setdefault ("year", datetime.now ().year)
        context.setdefault ("header_badge", context.get ("app_name") or appConfig.app_name)
        brand = await cls.mailBrandName ()
        if brand:
            context["app_name"] = brand
            context["header_badge"] = brand
        try:
            from src.app.bases.app_i18n import AppI18n
            i18n = AppI18n.i18n ()
            context.setdefault ("mail_user_information", i18n.t ("_v1_user.mail.user_information"))
            context.setdefault ("mail_full_name", i18n.t ("_v1_user.mail.full_name"))
            context.setdefault ("mail_email_address", i18n.t ("_v1_user.mail.email_address"))
            context.setdefault ("mail_thanks", i18n.t ("_v1_user.mail.thanks"))
            context.setdefault ("mail_rights", i18n.t ("_v1_user.mail.rights"))
        except Exception:
            context.setdefault ("mail_user_information", "User information")
            context.setdefault ("mail_full_name", "Full name")
            context.setdefault ("mail_email_address", "Email address")
            context.setdefault ("mail_thanks", "Thanks")
            context.setdefault ("mail_rights", "All rights reserved.")
        if not from_email:
            from_email = config.from_email
        if not from_name:
            from_name = config.from_name
        fromAddr = f"{from_name} <{from_email}>" if from_name else from_email
        if isinstance (to, str):
            to = [to]
        message = MIMEMultipart ("alternative")
        message["From"] = fromAddr
        message["To"] = ", ".join (to)
        message["Subject"] = subject
        if template:
            env = cls.jinjaEnv ()
            templatePath = Path (template)
            if templatePath.is_absolute () and templatePath.exists ():
                templateContent = templatePath.read_text (encoding="utf-8")
                templateObj = Template (templateContent)
            else:
                try:
                    templateObj = env.get_template (template)
                except Exception:
                    if templatePath.exists ():
                        templateContent = templatePath.read_text (encoding="utf-8")
                        templateObj = Template (templateContent)
                    else:
                        raise ValueError (f"Template not found: {template}")
            rendered = templateObj.render (**context)
            if template.endswith (".html") or template.endswith (".hbs"):
                html = rendered
            else:
                body = rendered
        if html:
            htmlPart = MIMEText (html, "html", "utf-8")
            message.attach (htmlPart)
        if body:
            textPart = MIMEText (body, "plain", "utf-8")
            message.attach (textPart)
        if attachments:
            for attachment in attachments:
                part = MIMEBase ("application", "octet-stream")
                if "path" in attachment:
                    with open (attachment["path"], "rb") as f:
                        part.set_payload (f.read ())
                elif "content" in attachment:
                    part.set_payload (attachment["content"])
                else:
                    continue
                encoders.encode_base64 (part)
                part.add_header (
                    "Content-Disposition",
                    f'attachment; filename="{attachment.get ("filename", "attachment")}"'
                )
                message.attach (part)
        try:
            await smtp.connect ()
            if config.username and config.password:
                await smtp.login (config.username, config.password)
            await smtp.send_message (message)
            await smtp.quit ()
            return True
        except Exception as e:
            logger.error (f"Error sending email: {e}", exc_info=True)
            return False
        finally:
            try:
                if smtp.is_connected:
                    await smtp.quit ()
            except Exception:
                logger.warning ("smtp quit failed", exc_info=True)
