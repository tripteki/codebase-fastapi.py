from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

class AppStatic:
    """
    AppStatic
    """
    @classmethod
    def boot (cls, app: FastAPI) -> None:
        """
        Args:
            cls
            app (FastAPI)
        Returns:
            None
        """
        storagePath = Path ("storage/disks/public")
        storagePath.mkdir (parents=True, exist_ok=True)

        app.mount ("/storage", StaticFiles (
            directory=storagePath
        ), name="storage")

        app.mount ("/", StaticFiles (
            directory=Path ("public/")
        ), name="static")
