from datetime import datetime
from typing import Optional
from src.app.bases.app_event_base import AppEventBase

class UserAdminDeactivatedEvent (AppEventBase):
    """
    UserAdminDeactivatedEvent (AppEventBase)

    Attributes:
        id (str)
        name (str)
        email (str)
        password (Optional[str])
        email_verified_at (Optional[datetime])
        created_at (datetime)
        updated_at (datetime)
        deleted_at (Optional[datetime])
    """
    id: str
    name: str
    email: str
    password: Optional[str] = None
    email_verified_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
