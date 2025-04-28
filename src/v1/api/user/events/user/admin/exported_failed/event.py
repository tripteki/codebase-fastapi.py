from src.app.bases.app_event_base import AppEventBase

class UserAdminExportedFailedEvent (AppEventBase):
    """
    UserAdminExportedFailedEvent
    """
    userId: str
    error: str
