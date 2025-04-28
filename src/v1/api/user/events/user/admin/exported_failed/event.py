from src.app.bases.app_event_base import AppEventBase

class UserAdminExportedFailedEvent (AppEventBase):
    """
    UserAdminExportedFailedEvent (AppEventBase)

    Attributes:
        userId (str)
        error (str)
    """
    userId: str
    error: str
