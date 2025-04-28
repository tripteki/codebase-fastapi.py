from pathlib import Path
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates

class AppView:
    """
    AppView
    """
    @classmethod
    def register (cls, app: FastAPI) -> Jinja2Templates:
        """
        Args:
            cls
            app (FastAPI)
        Returns:
            Jinja2Templates
        """
        return Jinja2Templates (
            directory=Path (__file__).parent.parent / "views/"
        )

    @classmethod
    def viewPath (cls) -> Path:
        """
        Args:
            cls
        Returns:
            Path
        """
        return Path (__file__).parent.parent / "views/"
