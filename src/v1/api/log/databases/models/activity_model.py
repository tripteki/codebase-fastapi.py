from datetime import datetime
from typing import Any, Dict, Optional
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON, Text
from ulid import ULID

class Activity (SQLModel, table=True):
    """
    Activity (SQLModel)

    Attributes:
        id (str)
        log_name (Optional[str])
        description (str)
        subject_type (Optional[str])
        event (Optional[str])
        subject_id (Optional[str])
        causer_type (Optional[str])
        causer_id (Optional[str])
        properties (Optional[Dict[str, Any]])
        batch_uuid (Optional[str])
        created_at (datetime)
        updated_at (datetime)
    """
    __tablename__ = "activity_log"

    id: str = Field (default_factory=lambda: str (ULID ()), primary_key=True)
    log_name: Optional[str] = Field (default=None, index=True)
    description: str = Field (sa_column=Column (Text, nullable=False))
    subject_type: Optional[str] = Field (default=None)
    event: Optional[str] = Field (default=None)
    subject_id: Optional[str] = Field (default=None)
    causer_type: Optional[str] = Field (default=None)
    causer_id: Optional[str] = Field (default=None)
    properties: Optional[Dict[str, Any]] = Field (default=None, sa_column=Column (JSON, nullable=True))
    batch_uuid: Optional[str] = Field (default=None)
    created_at: datetime = Field (default_factory=datetime.utcnow)
    updated_at: datetime = Field (default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})
