from src.app.bases.app_event_base import AppEventBase

class RoleAdminImportedFailedEvent (AppEventBase):
    """
    RoleAdminImportedFailedEvent (AppEventBase)

    Attributes:
        userId (str)
        filename (str)
        error (str)
    """
    userId: str
    filename: str
    error: str
