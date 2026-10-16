from src.app.bases.app_event_base import AppEventBase

class PermissionAdminImportedFailedEvent (AppEventBase):
    """
    PermissionAdminImportedFailedEvent (AppEventBase)

    Attributes:
        userId (str)
        filename (str)
        error (str)
    """
    userId: str
    filename: str
    error: str
