import logging
from fastapi import FastAPI
import asyncio
from src.app.bases.app_event import getEventEmitter
from src.app.utils.app_module_scanner import AppModuleScanner

logger = logging.getLogger (__name__)

class AppEventListener:
    """
    AppEventListener
    """
    @staticmethod
    def loadListeners (app: FastAPI) -> None:
        """
        Args:
            app (FastAPI)
        Returns:
            None
        """
        emitter = getEventEmitter ()
        try:
            loop = asyncio.get_event_loop ()
            emitter.setLoop (loop)
        except RuntimeError:
            loop = asyncio.new_event_loop ()
            asyncio.set_event_loop (loop)
            emitter.setLoop (loop)

        print ("[DEBUG] AppEventListener.loadListeners called", flush=True)

        def onModuleLoaded (moduleName: str) -> None:
            """
            Args:
                moduleName (str)
            Returns:
                None
            """
            logger.info (f"Event listeners loaded: {moduleName}")
            print (f"[DEBUG] Event listener module loaded: {moduleName}", flush=True)

        loaded = AppModuleScanner.scanModules ("listeners", callback=onModuleLoaded)
        logger.info (f"Loaded {len (loaded)} event listener module(s)")
        print (f"[DEBUG] Total event listener modules loaded: {len (loaded)}", flush=True)
