from src.app.bases.app_event_base import AppEventBase

class RoleAdminExportedFailedEvent (AppEventBase):
    """
    RoleAdminExportedFailedEvent (AppEventBase)

    Attributes:
        userId (str)
        error (str)
    """
    userId: str
    error: str
