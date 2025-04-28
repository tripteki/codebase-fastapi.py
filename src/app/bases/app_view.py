from typing import Any
from pathlib import Path
from fastapi.templating import Jinja2Templates

class AppView:
    """
    AppView
    """
    @classmethod
    def register (cls, app) -> Any:
        """
        Args:
            cls
            app (FastAPI)
        Returns:
            Jinja2Templates
        """
        return Jinja2Templates (
            directory=Path (__file__).resolve ().parents[1] / "views/"
        )
