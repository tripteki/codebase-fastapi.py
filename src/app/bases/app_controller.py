from pathlib import Path
from fastapi.templating import Jinja2Templates
from src.app.bases.app import App

class AppController (App):
    """
    AppController (App)

    Attributes:
        _view (None)
    """
    _view = None

    @staticmethod
    def view ():
        """
        Returns:
            Jinja2Templates
        """
        if AppController._view is None:
            AppController._view = Jinja2Templates (directory=Path (__file__).resolve ().parents[1] / "views/")
        return AppController._view
