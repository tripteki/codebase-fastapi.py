from __future__ import annotations

from datetime import datetime
from typing import Optional, Dict, TYPE_CHECKING
from typing_extensions import Self
from pydantic import BaseModel, Field
from src.v1.api.notification.databases.models.notification_model import Notification

if TYPE_CHECKING:
    from src.v1.api.user.dtos.user_transformer_dto import UserTransformerDto

class NotificationCountTransformerDto (BaseModel):
    """
    NotificationCountTransformerDto (BaseModel)

    Attributes:
        count (int)
    """
    count: int = Field (..., json_schema_extra={"example": 0})

class NotificationReadTransformerDto (BaseModel):
    """
    NotificationReadTransformerDto (BaseModel)

    Attributes:
        read (int)
    """
    read: int = Field (..., json_schema_extra={"example": 0})

class NotificationUnreadTransformerDto (BaseModel):
    """
    NotificationUnreadTransformerDto (BaseModel)

    Attributes:
        unread (int)
    """
    unread: int = Field (..., json_schema_extra={"example": 0})

class NotificationTransformerDto (BaseModel):
    """
    NotificationTransformerDto (BaseModel)

    Attributes:
        id (str)
        user_id (str)
        type (str)
        data (Dict[str, object])
        read_at (Optional[datetime])
        created_at (datetime)
        updated_at (datetime)
        deleted_at (Optional[datetime])
        user (Optional[UserTransformerDto])
    """
    id: str = Field (..., json_schema_extra={"example": "string"})
    user_id: str = Field (..., json_schema_extra={"example": "string"})
    type: str = Field (..., json_schema_extra={"example": "string"})
    data: Dict[str, object] = Field (..., json_schema_extra={"example": {}})
    read_at: Optional[datetime] = Field (None, json_schema_extra={"example": None})
    created_at: datetime = Field (..., json_schema_extra={"example": "string"})
    updated_at: datetime = Field (..., json_schema_extra={"example": "string"})
    deleted_at: Optional[datetime] = Field (None, json_schema_extra={"example": None})
    user: Optional[UserTransformerDto] = Field (None, json_schema_extra={"example": None})

    @staticmethod
    def fromNotification (notification: Notification) -> Self:
        """
        Args:
            notification (Notification)
        Returns:
            NotificationTransformerDto
        """
        return NotificationTransformerDto (
            id=notification.id,
            user_id=notification.user_id,
            type=notification.type,
            data=notification.data,
            read_at=notification.read_at,
            created_at=notification.created_at,
            updated_at=notification.updated_at,
            deleted_at=notification.deleted_at
        )

from src.v1.api.user.dtos.user_transformer_dto import UserTransformerDto
NotificationTransformerDto.model_rebuild ()
