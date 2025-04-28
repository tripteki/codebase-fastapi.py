from datetime import datetime
from typing import Optional
from src.app.bases.app_event_base import AppEventBase

class UserAuthResetEvent (AppEventBase):
    """
    UserAuthResetEvent (AppEventBase)

    Attributes:
        id (str)
        name (str)
        email (str)
        email_verified_at (Optional[datetime])
        created_at (datetime)
        updated_at (datetime)
        token (str)
    """
    id: str
    name: str
    email: str
    email_verified_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    token: str
