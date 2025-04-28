from src.app.bases.app_event_base import AppEventBase

class UserAdminImportedEvent (AppEventBase):
    """
    UserAdminImportedEvent (AppEventBase)

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
