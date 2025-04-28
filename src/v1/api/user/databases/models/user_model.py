from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from ulid import ULID

class UserBase (SQLModel):
    """
    UserBase (SQLModel)

    Attributes:
        name (str)
        email (str)
        password (str)
        email_verified_at (Optional[datetime])
    """
    name: str
    email: str = Field (unique=True, index=True)
    password: str
    email_verified_at: Optional[datetime] = None

class User (UserBase, table=True):
    """
    User (UserBase)

    Attributes:
        id (str)
        name (str)
        email (str)
        password (str)
        email_verified_at (Optional[datetime])
        deleted_at (Optional[datetime])
        created_at (datetime)
        updated_at (datetime)
    """
    __tablename__ = "users"
    id: str = Field (default_factory=lambda: str (ULID ()), primary_key=True)
    deleted_at: Optional[datetime] = Field (default=None)
    created_at: datetime = Field (default_factory=datetime.utcnow)
    updated_at: datetime = Field (default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})
