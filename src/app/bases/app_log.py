import logging.config
from typing import Any
from src.app.configs.log_config import LogConfig

class AppLog:
    """
    AppLog
    """
    @classmethod
    def register (cls, app) -> Any:
        """
        Args:
            cls
            app (FastAPI)
        Returns:
            Logger
        """
        logConfig = LogConfig.config ()

        logging.config.dictConfig (
            logConfig.log ()
        )
        return logging.getLogger (
            __name__
        )
