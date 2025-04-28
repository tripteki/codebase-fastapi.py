from datetime import datetime
from typing import Optional
from src.app.bases.app_event_base import AppEventBase

class UserAuthRegisteredEvent (AppEventBase):
    """
    UserAuthRegisteredEvent (AppEventBase)

    Attributes:
        id (str)
        name (str)
        email (str)
        password (Optional[str])
        email_verified_at (Optional[datetime])
        created_at (datetime)
        updated_at (datetime)
        deleted_at (Optional[datetime])
        token (Optional[str])
    """
    id: str
    name: str
    email: str
    password: Optional[str] = None
    email_verified_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    token: Optional[str] = None
