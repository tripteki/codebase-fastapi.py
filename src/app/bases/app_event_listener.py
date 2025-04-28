from pathlib import Path
from typing import Any
import asyncio
import importlib
import traceback
from src.app.bases.app_event import getEventEmitter

class AppEventListener:
    """
    AppEventListener
    """
    @staticmethod
    def loadListeners (app: Any) -> None:
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
        basePath = Path (".")
        srcPath = basePath / "src"
        if not srcPath.exists ():
            return
        for item in srcPath.iterdir ():
            if not item.is_dir () or not item.name.startswith ("v") or not item.name[1:].isdigit ():
                continue
            for subPath in ["api", "graphql"]:
                targetPath = item / subPath
                if not targetPath.exists ():
                    continue
                for moduleDir in targetPath.iterdir ():
                    if not moduleDir.is_dir () or moduleDir.name.startswith ("__"):
                        continue
                    listenersDir = moduleDir / "listeners"
                    if not listenersDir.exists ():
                        continue
                    for file in listenersDir.glob ("*.py"):
                        if file.name.startswith ("__"):
                            continue
                        relativePath = file.relative_to (basePath / "src")
                        moduleParts = list (relativePath.with_suffix ("").parts)
                        moduleName = "src." + ".".join (moduleParts)
                        try:
                            importlib.import_module (moduleName)
                            print (f"Event listeners loaded: {moduleName}.")
                        except Exception as e:
                            print (f"Warning: Could not load event listeners from {file.name}: {e}.")
