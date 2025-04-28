from src.app.bases.app_config import AppConfig

class DatabaseConfig (AppConfig):
    """
    DatabaseConfig (AppConfig)

    Attributes:
        database_postgre_uri (str)
        database_mongo_uri (str)
    """
    database_postgre_uri: str = ""
    database_mongo_uri: str = ""

    def postgre_uri (self) -> str:
        """
        Args:
            self
        Returns:
            str
        """
        if not self.database_postgre_uri:
            raise ValueError ("DATABASE_POSTGRE_URI is required")
        return self.database_postgre_uri

    def mongo_uri (self) -> str:
        """
        Args:
            self
        Returns:
            str
        """
        if not self.database_mongo_uri:
            raise ValueError ("DATABASE_MONGO_URI is required")
        return self.database_mongo_uri
