from src.app.bases.app_event_base import AppEventBase

class PermissionAdminImportedEvent (AppEventBase):
    """
    PermissionAdminImportedEvent (AppEventBase)

    Attributes:
        userId (str)
        filename (str)
        totalImported (int)
        totalSkipped (int)
    """
    userId: str
    filename: str
    totalImported: int
    totalSkipped: int
