from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Column, JSON
from ulid import ULID

class Profile (SQLModel, table=True):
    """
    Profile (SQLModel)

    Attributes:
        id (str)
        user_id (str)
        full_name (Optional[str])
        avatar (Optional[str])
        interests (Optional[List[str]])
        created_at (datetime)
        updated_at (datetime)
    """
    __tablename__ = "profiles"
    id: str = Field (default_factory=lambda: str (ULID ()), primary_key=True)
    user_id: str = Field (foreign_key="users.id", unique=True, index=True)
    full_name: Optional[str] = Field (default=None, max_length=255)
    avatar: Optional[str] = Field (default=None, max_length=255)
    interests: Optional[List[str]] = Field (default=None, sa_column=Column (JSON))
    created_at: datetime = Field (default_factory=datetime.utcnow)
    updated_at: datetime = Field (default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})
