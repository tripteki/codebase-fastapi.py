from __future__ import annotations

from typing import Optional, TYPE_CHECKING
from typing_extensions import Self
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
import logging
import redis.asyncio as cache_redis
from sqlalchemy import Engine
from motor.motor_asyncio import AsyncIOMotorClient
from rq import Queue
import aiosmtplib
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.app.bases.app_disk import AppDisk
from src.app.bases.app_event import getEventEmitter, AppEventEmitter
from src.app.bases.app_i18n import AppI18n
from src.app.bases.app_mail import AppMail
from src.app.bases.app_database import AppDatabase
from src.app.bases.app_queue import AppQueue
from src.app.bases.app_scheduler import AppScheduler
from src.app.configs.app_config import AppConfig
from src.app.configs.playground_config import PlaygroundConfig
from src.app.configs.swagger_config import SwaggerConfig

if TYPE_CHECKING:
    from src.app.bases.app_auth import AppAuth

class AppContext:
    """
    AppContext

    Attributes:
        _instance (Optional[Self])
        _app (Optional[FastAPI])
        _appConfig (Optional[AppConfig])
        _swaggerConfig (Optional[SwaggerConfig])
        _playgroundConfig (Optional[PlaygroundConfig])
    """
    _instance: Optional[Self] = None
    _app: Optional[FastAPI] = None
    _appConfig: Optional[AppConfig] = None
    _swaggerConfig: Optional[SwaggerConfig] = None
    _playgroundConfig: Optional[PlaygroundConfig] = None

    def __init__ (self) -> None:
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
    def instance (cls) -> Self:
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
    def setApp (cls, app: FastAPI) -> None:
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
    def getApp (cls) -> Optional[FastAPI]:
        """
        Args:
            cls
        Returns:
            Optional[FastAPI]
        """
        return cls.instance ()._app

    @classmethod
    def appConfig (cls) -> AppConfig:
        """
        Args:
            cls
        Returns:
            AppConfig
        """
        return cls.instance ()._appConfig

    @classmethod
    def swaggerConfig (cls) -> SwaggerConfig:
        """
        Args:
            cls
        Returns:
            SwaggerConfig
        """
        return cls.instance ()._swaggerConfig

    @classmethod
    def playgroundConfig (cls) -> PlaygroundConfig:
        """
        Args:
            cls
        Returns:
            PlaygroundConfig
        """
        return cls.instance ()._playgroundConfig

    @classmethod
    def log (cls) -> Optional[logging.Logger]:
        """
        Args:
            cls
        Returns:
            Optional[logging.Logger]
        """
        app = cls.getApp ()
        if app and hasattr (app.state, "log"):
            return app.state.log
        return None

    @classmethod
    def view (cls) -> Optional[Jinja2Templates]:
        """
        Args:
            cls
        Returns:
            Optional[Jinja2Templates]
        """
        app = cls.getApp ()
        if app and hasattr (app.state, "view"):
            return app.state.view
        return None

    @classmethod
    def cacheRedis (cls) -> Optional[cache_redis.Redis]:
        """
        Args:
            cls
        Returns:
            Optional[cache_redis.Redis]
        """
        app = cls.getApp ()
        if app and hasattr (app.state, "cacheRedis"):
            return app.state.cacheRedis
        return None

    @classmethod
    def databasePostgresql (cls) -> Engine:
        """
        Args:
            cls
        Returns:
            Engine
        """
        return AppDatabase.databasePostgresql ()

    @classmethod
    def databaseMongonosql (cls) -> Optional[AsyncIOMotorClient]:
        """
        Args:
            cls
        Returns:
            Optional[AsyncIOMotorClient]
        """
        return AppDatabase.databaseMongonosql ()

    @classmethod
    def eventEmitter (cls) -> AppEventEmitter:
        """
        Args:
            cls
        Returns:
            AppEventEmitter
        """
        return getEventEmitter ()

    @classmethod
    def queue (cls, queueName: str) -> Queue:
        """
        Args:
            cls
            queueName (str)
        Returns:
            Queue
        """
        return AppQueue.getQueue (queueName)

    @classmethod
    def mail (cls) -> aiosmtplib.SMTP:
        """
        Args:
            cls
        Returns:
            aiosmtplib.SMTP
        """
        return AppMail.mail ()

    @classmethod
    def i18n (cls) -> AppI18n:
        """
        Args:
            cls
        Returns:
            AppI18n
        """
        return AppI18n.i18n ()

    @classmethod
    def disk (cls) -> type[AppDisk]:
        """
        Args:
            cls
        Returns:
            type[AppDisk]
        """
        return AppDisk

    @classmethod
    def scheduler (cls) -> AsyncIOScheduler:
        """
        Args:
            cls
        Returns:
            AsyncIOScheduler
        """
        return AppScheduler.scheduler ()

    @classmethod
    def auth (cls) -> type[AppAuth]:
        """
        Args:
            cls
        Returns:
            type[AppAuth]
        """
        from src.app.bases.app_auth import AppAuth
        return AppAuth
