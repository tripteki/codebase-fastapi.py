import logging
from src.app.utils.app_module_scanner import AppModuleScanner

logger = logging.getLogger (__name__)

class AppScheduleLoader:
    """
    AppScheduleLoader
    """
    @staticmethod
    def loadSchedules () -> None:
        """
        Returns:
            None
        """
        def onModuleLoaded (moduleName: str) -> None:
            """
            Args:
                moduleName (str)
            Returns:
                None
            """
            logger.info (f"Schedule service loaded: {moduleName}")

        loaded = AppModuleScanner.scanModules ("services", callback=onModuleLoaded, pattern="*schedule*.py")
        logger.info (f"Loaded {len (loaded)} schedule service module(s)")
