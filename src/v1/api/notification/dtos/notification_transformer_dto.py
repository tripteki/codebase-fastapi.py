from datetime import datetime
from typing import Optional, Dict, Any, TYPE_CHECKING
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from src.v1.api.user.dtos.user_transformer_dto import UserTransformerDto

class NotificationCountTransformerDto (BaseModel):
    """
    NotificationCountTransformerDto
    """
    count: int = Field (..., json_schema_extra={"example": 0})

class NotificationReadTransformerDto (BaseModel):
    """
    NotificationReadTransformerDto
    """
    read: int = Field (..., json_schema_extra={"example": 0})

class NotificationUnreadTransformerDto (BaseModel):
    """
    NotificationUnreadTransformerDto
    """
    unread: int = Field (..., json_schema_extra={"example": 0})

class NotificationTransformerDto (BaseModel):
    """
    NotificationTransformerDto
    """
    id: str = Field (..., json_schema_extra={"example": "string"})
    user_id: str = Field (..., json_schema_extra={"example": "string"})
    type: str = Field (..., json_schema_extra={"example": "string"})
    data: Dict[str, Any] = Field (..., json_schema_extra={"example": {}})
    read_at: Optional[datetime] = Field (None, json_schema_extra={"example": None})
    created_at: datetime = Field (..., json_schema_extra={"example": "string"})
    updated_at: datetime = Field (..., json_schema_extra={"example": "string"})
    deleted_at: Optional[datetime] = Field (None, json_schema_extra={"example": None})
    user: Optional["UserTransformerDto"] = Field (None, json_schema_extra={"example": None})

from src.v1.api.user.dtos.user_transformer_dto import UserTransformerDto
NotificationTransformerDto.model_rebuild ()
