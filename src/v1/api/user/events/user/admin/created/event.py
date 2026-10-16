from src.app.bases.app_event_base import AppEventBase

class UserAdminCreatedEvent (AppEventBase):
    """
    UserAdminCreatedEvent (AppEventBase)

    Attributes:
        id (str)
        name (str)
        email (str)
        roleLabel (str)
    """
    id: str
    name: str
    email: str
    roleLabel: str
