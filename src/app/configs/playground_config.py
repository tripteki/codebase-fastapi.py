from src.app.bases.app_config import AppConfig

class PlaygroundConfig (AppConfig):
    """
    PlaygroundConfig (AppConfig)

    Attributes:
        playground_path (str)
        playground_description (str)
    """
    playground_path: str = "graphql"
    playground_description: str = "Documentation Description"
