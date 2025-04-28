from typing import Dict
from fastapi import APIRouter, Depends
from fastapi_limiter.depends import RateLimiter
from src.app.configs.app_config import AppConfig

appRouter = APIRouter (prefix="/api")

class AppController:
    """
    AppController
    """
    @staticmethod
    @appRouter.get (
        "/version",
        tags=["Status"],
        dependencies=[Depends (RateLimiter (times=5, seconds=5))]
    )
    def version () -> Dict[str, str]:
        """
        Show Version
        """
        appConfig = AppConfig.config ()

        return {
            "version": appConfig.app_version,
        }
