from src.app.bases.app_event_base import AppEventBase

class UserAdminExportedEvent (AppEventBase):
    """
    UserAdminExportedEvent (AppEventBase)

    Attributes:
        userId (str)
        filename (str)
        fileUrl (str)
        filePath (str)
    """
    userId: str
    filename: str
    fileUrl: str
    filePath: str
