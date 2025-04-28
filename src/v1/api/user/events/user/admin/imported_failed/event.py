from src.app.bases.app_event_base import AppEventBase

class UserAdminImportedFailedEvent (AppEventBase):
    """
    UserAdminImportedFailedEvent
    """
    userId: str
    filename: str
    error: str
