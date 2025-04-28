from src.app.bases.app_config import AppConfig

class SwaggerConfig (AppConfig):
    """
    SwaggerConfig (AppConfig)

    Attributes:
        swagger_path (str)
        swagger_description (str)
    """
    swagger_path: str = "api/docs"
    swagger_description: str = "Documentation Description"
