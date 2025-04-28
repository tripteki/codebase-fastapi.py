import logging.config
from src.app.configs.app_config import AppConfig
from src.app.configs.swagger_config import SwaggerConfig
from src.app.configs.playground_config import PlaygroundConfig
from src.app.configs.log_config import LogConfig

class App:
    """
    App

    Attributes:
        _appConfig (None)
        _swaggerConfig (None)
        _playgroundConfig (None)
        _logConfig (None)
        _log (None)
    """
    _appConfig = None
    _swaggerConfig = None
    _playgroundConfig = None
    _logConfig = None
    _log = None

    @staticmethod
    def appConfig ():
        """
        Returns:
            AppConfig
        """
        if App._appConfig is None:
            App._appConfig = AppConfig.config ()
        return App._appConfig

    @staticmethod
    def swaggerConfig ():
        """
        Returns:
            SwaggerConfig
        """
        if App._swaggerConfig is None:
            App._swaggerConfig = SwaggerConfig.config ()
        return App._swaggerConfig

    @staticmethod
    def playgroundConfig ():
        """
        Returns:
            PlaygroundConfig
        """
        if App._playgroundConfig is None:
            App._playgroundConfig = PlaygroundConfig.config ()
        return App._playgroundConfig

    @staticmethod
    def logConfig ():
        """
        Returns:
            LogConfig
        """
        if App._logConfig is None:
            App._logConfig = LogConfig.config ()
        return App._logConfig

    @staticmethod
    def log ():
        """
        Returns:
            Logger
        """
        if App._log is None:
            logging.config.dictConfig (App.logConfig ().log ())
            App._log = logging.getLogger (__name__)
        return App._log
