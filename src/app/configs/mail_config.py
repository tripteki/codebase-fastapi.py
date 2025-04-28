from src.app.bases.app_config import AppConfig

class MailConfig (AppConfig):
    """
    MailConfig (AppConfig)

    Attributes:
        host (str)
        port (int)
        username (str)
        password (str)
        from_email (str)
        from_name (str)
        secure (bool)
        tls (bool)
    """
    host: str = ""
    port: int = 587
    username: str = ""
    password: str = ""
    from_email: str = ""
    from_name: str = ""
    secure: bool = False
    tls: bool = True
