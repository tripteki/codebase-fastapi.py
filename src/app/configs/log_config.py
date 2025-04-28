from typing import Dict
from src.app.bases.app_config import AppConfig

class LogConfig (AppConfig):
    """
    LogConfig (AppConfig)

    Attributes:
        log_level (str)
    """
    log_level: str = "DEBUG"

    def log (self) -> Dict[str, object]:
        """
        Args:
            self
        Returns:
            Dict[str, object]
        """
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "[%(asctime)s.%(msecs)03d] %(levelname)s [%(thread)d] - %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                },
            },
            "handlers": {
                "console": {
                    "level": self.log_level,
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "stream": "ext://sys.stdout",
                },
                "file": {
                    "level": self.log_level,
                    "class": "logging.handlers.TimedRotatingFileHandler",
                    "formatter": "default",
                    "filename": "storage/logs/fastapi.log",
                    "when": "midnight",
                    "interval": 1,
                    "backupCount": 7,
                    "encoding": "utf-8",
                },
            },
            "root": {
                "level": self.log_level,
                "handlers": ["console", "file"],
            },
        }
