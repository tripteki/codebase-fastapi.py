from pathlib import Path
from typing import List, Callable, Optional
import importlib
import logging

logger = logging.getLogger (__name__)

class AppModuleScanner:
    """
    AppModuleScanner
    """
    @staticmethod
    def scanModules (
        target_dir: str,
        callback: Optional[Callable[[str], None]] = None,
        pattern: str = "*.py"
    ) -> List[str]:
        """
        Args:
            target_dir (str)
            callback (Optional[Callable[[str], None]])
            pattern (str)
        Returns:
            List[str]
        """
        loaded_modules: List[str] = []
        basePath = Path (".")
        srcPath = basePath / "src"

        if not srcPath.exists ():
            return loaded_modules

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

                    scanDir = moduleDir / target_dir
                    if not scanDir.exists ():
                        continue

                    files = scanDir.glob (pattern)

                    for file in files:
                        if file.name.startswith ("__"):
                            continue

                        relativePath = file.relative_to (basePath / "src")
                        moduleParts = list (relativePath.with_suffix ("").parts)
                        moduleName = "src." + ".".join (moduleParts)

                        try:
                            importlib.import_module (moduleName)
                            loaded_modules.append (moduleName)

                            if callback:
                                callback (moduleName)
                            else:
                                logger.info (f"Module loaded: {moduleName}")

                        except Exception as e:
                            logger.warning (
                                f"Could not load module from {file.name}: {e}",
                                exc_info=True
                            )

        return loaded_modules
