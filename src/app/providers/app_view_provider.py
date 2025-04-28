from pathlib import Path
from fastapi.staticfiles import StaticFiles
from src.app.bases.app_provider import AppProvider

class AppViewProvider (AppProvider):
    """
    AppViewProvider (AppProvider)
    """
    @staticmethod
    def register (app) -> None:
        """
        Args:
            app (FastAPI)
        Returns:
            None
        """
        pass

    @staticmethod
    def boot (app) -> None:
        """
        Args:
            app (FastAPI)
        Returns:
            None
        """
        AppViewProvider.bootPath (app)

    @staticmethod
    def bootPath (app) -> None:
        """
        Args:
            app (FastAPI)
        Returns:
            None
        """
        app.mount ("/", StaticFiles (directory=Path (__file__).resolve ().parents[3] / "public/"), name="static")
