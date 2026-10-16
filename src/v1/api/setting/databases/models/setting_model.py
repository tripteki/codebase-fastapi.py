from datetime import datetime
from typing import Optional
from sqlalchemy import Text
from sqlmodel import SQLModel, Field, Column
from ulid import ULID

class Setting (SQLModel, table=True):
    """
    Setting (SQLModel)

    Attributes:
        id (str)
        key (str)
        value (Optional[str])
        value_kind (str)
        created_at (datetime)
        updated_at (datetime)
        deleted_at (Optional[datetime])
    """
    __tablename__ = "settings"

    id: str = Field (default_factory=lambda: str (ULID ()), primary_key=True)
    key: str = Field (index=True, unique=True, max_length=255)
    value: Optional[str] = Field (default=None, sa_column=Column (Text, nullable=True))
    value_kind: str = Field (default="text", max_length=16)
    created_at: datetime = Field (default_factory=datetime.utcnow)
    updated_at: datetime = Field (default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})
    deleted_at: Optional[datetime] = Field (default=None)
