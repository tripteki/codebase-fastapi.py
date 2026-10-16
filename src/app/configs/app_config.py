from typing import List
from urllib.parse import urlparse
from pydantic import AliasChoices, Field
from src.app.bases.app_config import AppConfig
from src.app.helpers.package_helper import packageHelper

class AppConfig (AppConfig):
    """
    AppConfig (AppConfig)

    Attributes:
        app_name (str)
        app_secret (str)
        app_version (str)
        app_env (str)
        app_host (str)
        app_port (int)
        app_email_server (str)
        app_url (str)
        frontend_url (str)
        cors_origin (List[str])
        cors_methods (List[str])
        cors_allowed_headers (List[str])
        cors_exposed_headers (List[str])
        cors_min_age (int)
        cors_max_age (int)
        cors_credential (bool)
        timezone (str)
        datetime_format (str)
        locale (str)
        faker_locale (str)
        fallback_locale (str)
    """
    app_name: str = packageHelper ("name")
    app_secret: str = ""
    app_version: str = packageHelper ("version")
    app_env: str = "production"
    app_host: str = "0.0.0.0"
    app_port: int = 3000
    app_email_server: str = ""
    app_url: str = ""
    frontend_url: str = "http://localhost:3000"
    cors_origin: List[str] = ["http://localhost:3000"]
    cors_methods: List[str] = ["POST", "PUT", "PATCH", "DELETE", "GET", "HEAD"]
    cors_allowed_headers: List[str] = ["*"]
    cors_exposed_headers: List[str] = []
    cors_min_age: int = 0
    cors_max_age: int = 0
    cors_credential: bool = False
    timezone: str = Field ("UTC", validation_alias=AliasChoices ("APP_TIMEZONE", "TIMEZONE"))
    datetime_format: str = Field ("YYYY-MM-DD HH:mm:ss", validation_alias=AliasChoices ("APP_DATETIME_FORMAT", "DATETIME_FORMAT"))
    locale: str = Field ("en", validation_alias=AliasChoices ("APP_LOCALE", "LOCALE"))
    faker_locale: str = Field ("en", validation_alias=AliasChoices ("APP_FAKER_LOCALE", "FAKER_LOCALE"))
    fallback_locale: str = Field ("en", validation_alias=AliasChoices ("APP_FALLBACK_LOCALE", "FALLBACK_LOCALE"))

    def email_server (self) -> str:
        """
        Returns:
            str
        """
        override = (self.app_email_server or "").strip ()
        if override:
            return override
        url = (self.app_url or "").strip ()
        if not url:
            return ""
        parsed = urlparse (url if "://" in url else f"http://{url}")
        host = parsed.hostname or ""
        return host
