from pathlib import Path
from typing import Optional, List, Dict
import aiosmtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Environment, FileSystemLoader, Template
import logging
from src.app.bases.app_view import AppView
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
            use_tls=config.tls,
            start_tls=config.tls
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
        smtp = cls.smtp ()
        context = context or {}
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
            logger = logging.getLogger (__name__)
            logger.error (f"Error sending email: {e}", exc_info=True)
            return False
        finally:
            try:
                if smtp.is_connected:
                    await smtp.quit ()
            except Exception:
                pass
