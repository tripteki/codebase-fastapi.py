from datetime import datetime
from typing import Optional
from src.app.bases.app_event_base import AppEventBase

class UserAuthRefreshedEvent (AppEventBase):
    """
    UserAuthRefreshedEvent (AppEventBase)

    Attributes:
        id (str)
        name (Optional[str])
        email (Optional[str])
        password (Optional[str])
        email_verified_at (Optional[datetime])
        created_at (Optional[datetime])
        updated_at (Optional[datetime])
        deleted_at (Optional[datetime])
    """
    id: str
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    email_verified_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
