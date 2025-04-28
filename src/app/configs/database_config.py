from src.app.bases.app_config import AppConfig

class DatabaseConfig (AppConfig):
    """
    DatabaseConfig (AppConfig)

    Attributes:
        postgre_uri (str)
    """
    postgre_uri: str = ""
