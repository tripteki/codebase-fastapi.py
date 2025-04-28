from src.app.bases.app_config import AppConfig

class AuthConfig (AppConfig):
    """
    AuthConfig (AppConfig)

    Attributes:
        jwt_secret (str)
        jwt_algorithm (str)
        jwt_access_token_expire_minutes (int)
        jwt_refresh_token_expire_days (int)
        jwt_issuer (str)
        jwt_audience (str)
    """
    jwt_secret: str = ""
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    jwt_refresh_token_expire_days: int = 30
    jwt_issuer: str = ""
    jwt_audience: str = ""

    def jwtSecret (self) -> str:
        """
        Args:
            self
        Returns:
            str
        """
        if self.jwt_secret:
            return self.jwt_secret
        return self.app_secret
