from typing import List
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
    frontend_url: str = "http://localhost:3000"
    cors_origin: List[str] = ["http://localhost:3000"]
    cors_methods: List[str] = ["POST", "PUT", "PATCH", "DELETE", "GET", "HEAD"]
    cors_allowed_headers: List[str] = ["*"]
    cors_exposed_headers: List[str] = []
    cors_min_age: int = 0
    cors_max_age: int = 0
    cors_credential: bool = False
    timezone: str = "UTC"
    datetime_format: str = "YYYY-MM-DD HH:mm:ss"
    locale: str = "en"
    faker_locale: str = "en"
    fallback_locale: str = "en"
