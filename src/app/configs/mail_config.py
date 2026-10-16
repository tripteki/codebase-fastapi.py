from typing_extensions import Self
from urllib.parse import unquote, urlparse
from pydantic import AliasChoices, Field, model_validator
from src.app.bases.app_config import AppConfig

class MailConfig (AppConfig):
    """
    MailConfig (AppConfig)

    Attributes:
        mail_uri (str)
        host (str)
        port (int)
        username (str)
        password (str)
        from_email (str)
        from_name (str)
        secure (bool)
        tls (bool)
    """
    mail_uri: str = ""
    host: str = Field ("", validation_alias=AliasChoices ("MAIL_HOST", "HOST"))
    port: int = Field (587, validation_alias=AliasChoices ("MAIL_PORT", "PORT"))
    username: str = Field ("", validation_alias=AliasChoices ("MAIL_USERNAME", "USERNAME"))
    password: str = Field ("", validation_alias=AliasChoices ("MAIL_PASSWORD", "PASSWORD"))
    from_email: str = Field ("", validation_alias=AliasChoices ("MAIL_FROM_EMAIL", "FROM_EMAIL"))
    from_name: str = Field ("", validation_alias=AliasChoices ("MAIL_FROM_NAME", "FROM_NAME"))
    secure: bool = Field (False, validation_alias=AliasChoices ("MAIL_SECURE", "SECURE"))
    tls: bool = Field (True, validation_alias=AliasChoices ("MAIL_TLS", "TLS"))

    @model_validator (mode="after")
    def applyMailUri (self) -> Self:
        """
        Args:
            self
        Returns:
            MailConfig
        """
        parsed = urlparse ((self.mail_uri or "").strip ())
        if parsed.hostname:
            self.secure = (parsed.scheme or "smtp").lower () in ("smtps", "smtp+ssl")
            self.host = parsed.hostname
            self.port = int (parsed.port) if parsed.port is not None else (465 if self.secure else 587)
            self.username = unquote (parsed.username or "")
            self.password = unquote (parsed.password or "")
        if self.secure:
            self.tls = False
        self.from_email = self.from_email.strip ()
        if not self.from_email and "@" in self.username:
            self.from_email = self.username
        return self

    def isConfigured (self) -> bool:
        """
        Args:
            self
        Returns:
            bool
        """
        return bool (self.host)
