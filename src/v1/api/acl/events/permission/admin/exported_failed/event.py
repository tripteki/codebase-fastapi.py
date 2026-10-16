from src.app.bases.app_event_base import AppEventBase

class PermissionAdminExportedFailedEvent (AppEventBase):
    """
    PermissionAdminExportedFailedEvent (AppEventBase)

    Attributes:
        userId (str)
        error (str)
    """
    userId: str
    error: str
