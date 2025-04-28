from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Text
from sqlmodel import SQLModel, Field, Relationship, Column, JSON
from ulid import ULID

class Notification (SQLModel, table=True):
    """
    Notification
    """
    __tablename__ = "notifications"
    id: str = Field (primary_key=True, default_factory=lambda: str (ULID ()))
    user_id: str = Field (foreign_key="users.id", index=True)
    type: str = Field (max_length=255)
    data: Dict[str, Any] = Field (sa_column=Column (JSON))
    read_at: Optional[datetime] = None
    created_at: datetime = Field (default_factory=datetime.utcnow)
    updated_at: datetime = Field (default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = None
