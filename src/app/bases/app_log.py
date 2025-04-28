from datetime import datetime
from pathlib import Path
from fastapi import FastAPI
import logging
import logging.config
from src.app.configs.log_config import LogConfig

class AppLog:
    """
    AppLog
    """
    @classmethod
    def register (cls, app: FastAPI) -> logging.Logger:
        """
        Args:
            cls
            app (FastAPI)
        Returns:
            Logger
        """
        logConfig = LogConfig.config ()
        logDict = logConfig.log ()
        dateStr = datetime.now ().strftime ("%Y-%m-%d")
        logDir = Path ("storage/logs")
        logDir.mkdir (parents=True, exist_ok=True)
        logFile = logDir / f"fastapi.log.{dateStr}"
        if "handlers" in logDict and "file" in logDict["handlers"]:
            logDict["handlers"]["file"]["filename"] = str (logFile)
        logFile.touch ()
        logging.config.dictConfig (logDict)
        return logging.getLogger (
            __name__
        )
