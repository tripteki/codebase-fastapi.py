from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field

USER_WEBPUSH_SUBSCRIBABLE_TYPE = "App\\Models\\User"

class PushSubscription (SQLModel, table=True):
    """
    PushSubscription (SQLModel)

    Attributes:
        id (int)
        subscribable_id (str)
        subscribable_type (str)
        endpoint (str)
        public_key (Optional[str])
        auth_token (Optional[str])
        content_encoding (Optional[str])
        created_at (datetime)
        updated_at (datetime)
    """
    __tablename__ = "push_subscriptions"
    id: Optional[int] = Field (default=None, primary_key=True)
    subscribable_id: str = Field (max_length=26, index=False)
    subscribable_type: str = Field (max_length=255)
    endpoint: str = Field (max_length=500, unique=True)
    public_key: Optional[str] = None
    auth_token: Optional[str] = None
    content_encoding: Optional[str] = None
    created_at: datetime = Field (default_factory=datetime.utcnow)
    updated_at: datetime = Field (default_factory=datetime.utcnow)
