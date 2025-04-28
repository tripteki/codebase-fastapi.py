from typing import Dict
from fastapi import APIRouter
from src.app.bases.app_controller import AppController

appRouter = APIRouter (prefix="/api")

class AppController (AppController):
    """
    AppController (AppController)
    """
    @staticmethod
    @appRouter.get (
        "/version",
        tags=["Status"]
    )
    def version () -> Dict[str, str]:
        """
        Show Version
        """
        return {
            "version": AppController.appConfig ().app_version,
        }
