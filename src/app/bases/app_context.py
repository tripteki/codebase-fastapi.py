from typing import Any, Optional
from src.app.bases.app_disk import AppDisk
from src.app.bases.app_event import getEventEmitter
from src.app.bases.app_i18n import AppI18n
from src.app.bases.app_mail import AppMail
from src.app.bases.app_database import AppDatabase
from src.app.bases.app_queue import AppQueue
from src.app.bases.app_scheduler import AppScheduler
from src.app.configs.app_config import AppConfig
from src.app.configs.playground_config import PlaygroundConfig
from src.app.configs.swagger_config import SwaggerConfig

class AppContext:
    """
    AppContext
    """
    _instance: Optional["AppContext"] = None
    _app: Any = None
    _appConfig: Any = None
    _swaggerConfig: Any = None
    _playgroundConfig: Any = None

    def __init__ (self):
        """
        Args:
            self
        Returns:
            None
        """
        if AppContext._instance is not None:
            raise RuntimeError ("AppContext is a singleton. Use AppContext.instance () instead.")

        self._appConfig = AppConfig.config ()
        self._swaggerConfig = SwaggerConfig.config ()
        self._playgroundConfig = PlaygroundConfig.config ()

    @classmethod
    def instance (cls) -> "AppContext":
        """
        Args:
            cls
        Returns:
            AppContext
        """
        if cls._instance is None:
            cls._instance = cls.__new__ (cls)
            cls._instance._appConfig = AppConfig.config ()
            cls._instance._swaggerConfig = SwaggerConfig.config ()
            cls._instance._playgroundConfig = PlaygroundConfig.config ()
        return cls._instance

    @classmethod
    def setApp (cls, app: Any) -> None:
        """
        Args:
            cls
            app (FastAPI)
        Returns:
            None
        """
        instance = cls.instance ()
        instance._app = app

    @classmethod
    def getApp (cls) -> Any:
        """
        Args:
            cls
        Returns:
            Any
        """
        return cls.instance ()._app

    @classmethod
    def appConfig (cls) -> Any:
        """
        Args:
            cls
        Returns:
            Any
        """
        return cls.instance ()._appConfig

    @classmethod
    def swaggerConfig (cls) -> Any:
        """
        Args:
            cls
        Returns:
            Any
        """
        return cls.instance ()._swaggerConfig

    @classmethod
    def playgroundConfig (cls) -> Any:
        """
        Args:
            cls
        Returns:
            Any
        """
        return cls.instance ()._playgroundConfig

    @classmethod
    def log (cls) -> Any:
        """
        Args:
            cls
        Returns:
            Any
        """
        app = cls.getApp ()
        if app and hasattr (app.state, "log"):
            return app.state.log
        return None

    @classmethod
    def view (cls) -> Any:
        """
        Args:
            cls
        Returns:
            Any
        """
        app = cls.getApp ()
        if app and hasattr (app.state, "view"):
            return app.state.view
        return None

    @classmethod
    def cacheRedis (cls) -> Any:
        """
        Args:
            cls
        Returns:
            Any
        """
        app = cls.getApp ()
        if app and hasattr (app.state, "cacheRedis"):
            return app.state.cacheRedis
        return None

    @classmethod
    def databasePostgresql (cls) -> Any:
        """
        Args:
            cls
        Returns:
            Any (Engine)
        """
        return AppDatabase.databasePostgresql ()

    @classmethod
    def databaseMongonosql (cls) -> Any:
        """
        Args:
            cls
        Returns:
            Any (AsyncIOMotorClient)
        """
        return AppDatabase.databaseMongonosql ()

    @classmethod
    def eventEmitter (cls) -> Any:
        """
        Args:
            cls
        Returns:
            Any
        """

    @classmethod
    def queue (cls, queueName: str) -> Any:
        """
        Args:
            cls
            queueName (str)
        Returns:
            Any
        """

    @classmethod
    def mail (cls) -> Any:
        """
        Args:
            cls
        Returns:
            Any
        """

    @classmethod
    def i18n (cls) -> Any:
        """
        Args:
            cls
        Returns:
            Any
        """

    @classmethod
    def disk (cls) -> Any:
        """
        Args:
            cls
        Returns:
            Any
        """

    @classmethod
    def scheduler (cls) -> Any:
        """
        Args:
            cls
        Returns:
            Any
        """

    @classmethod
    def auth (cls) -> Any:
        """
        Args:
            cls
        Returns:
            Any
        """
