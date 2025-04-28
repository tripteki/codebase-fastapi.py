from pathlib import Path
import importlib

class AppScheduleLoader:
    """
    AppScheduleLoader
    """
    @staticmethod
    def loadSchedules () -> None:
        """
        Args:
        Returns:
            None
        """
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

                    servicesDir = moduleDir / "services"
                    if not servicesDir.exists ():
                        continue

                    for file in servicesDir.glob ("*schedule*.py"):
                        if file.name.startswith ("__"):
                            continue

                        relativePath = file.relative_to (basePath / "src")
                        moduleParts = list (relativePath.with_suffix ("").parts)
                        moduleName = "src." + ".".join (moduleParts)

                        try:
                            importlib.import_module (moduleName)
                            print (f"Schedule service loaded: {moduleName}.")
                        except Exception as e:
                            print (f"Warning: Could not load schedule service from {file.name}: {e}.")
