from pathlib import Path
from src.app.bases.app_config import AppConfig

class DiskConfig (AppConfig):
    """
    DiskConfig (AppConfig)

    Attributes:
        disk_path (str)
        disk_public_path (str)
        disk_private_path (str)
    """
    disk_path: str = "storage/disks"
    disk_public_path: str = "storage/disks/public"
    disk_private_path: str = "storage/disks/private"

    def public_url (self) -> str:
        """
        Args:
            self
        Returns:
            str
        """
        app_url = getattr (self, "app_url", "http://localhost:8000")
        return f"{app_url}/storage"
