from datetime import datetime
from typing import Optional
from src.app.bases.app_event_base import AppEventBase

class UserAuthRefreshedEvent (AppEventBase):
    """
    UserAuthRefreshedEvent
    """
    id: str
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    email_verified_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
