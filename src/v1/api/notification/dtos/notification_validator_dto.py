from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class NotificationIdentifierDto (BaseModel):
    """
    NotificationIdentifierDto
    """
    id: str = Field (..., json_schema_extra={"example": "01HZGXQZJQK9X5Y7Z8W9V0U1T2"})

class NotificationUpdateValidatorDto (BaseModel):
    """
    NotificationUpdateValidatorDto
    """
    type: Optional[str] = Field (None, max_length=255, json_schema_extra={"example": "info"})
    data: Optional[Dict[str, Any]] = Field (None, json_schema_extra={"example": {"title": "Update", "body": "Content updated successfully"}})

class NotificationCreateValidatorDto (BaseModel):
    """
    NotificationCreateValidatorDto
    """
    user_id: str = Field (..., json_schema_extra={"example": "01HZGXQZJQK9X5Y7Z8W9V0U1T2"})
    type: str = Field (..., max_length=255, json_schema_extra={"example": "info"})
    data: Dict[str, Any] = Field (..., json_schema_extra={"example": {"title": "Welcome", "body": "Welcome to our platform"}})
