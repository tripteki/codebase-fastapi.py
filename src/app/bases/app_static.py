from pathlib import Path
from fastapi.staticfiles import StaticFiles

class AppStatic:
    """
    AppStatic
    """
    @classmethod
    def boot (cls, app) -> None:
        """
        Args:
            cls
            app (FastAPI)
        Returns:
            None
        """
        app.mount ("/", StaticFiles (
            directory=Path (__file__).resolve ().parents[3] / "public/"
        ), name="static")
