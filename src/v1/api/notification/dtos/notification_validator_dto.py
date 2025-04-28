from typing import Optional, Dict
from pydantic import BaseModel, Field

class NotificationIdentifierDto (BaseModel):
    """
    NotificationIdentifierDto (BaseModel)

    Attributes:
        id (str)
    """
    id: str = Field (..., json_schema_extra={"example": "01HZGXQZJQK9X5Y7Z8W9V0U1T2"})

class NotificationUpdateValidatorDto (BaseModel):
    """
    NotificationUpdateValidatorDto (BaseModel)

    Attributes:
        type (Optional[str])
        data (Optional[Dict[str, object]])
    """
    type: Optional[str] = Field (None, max_length=255, json_schema_extra={"example": "info"})
    data: Optional[Dict[str, object]] = Field (None, json_schema_extra={"example": {"title": "Update", "body": "Content updated successfully"}})

class NotificationCreateValidatorDto (BaseModel):
    """
    NotificationCreateValidatorDto (BaseModel)

    Attributes:
        user_id (str)
        type (str)
        data (Dict[str, object])
    """
    user_id: str = Field (..., json_schema_extra={"example": "01HZGXQZJQK9X5Y7Z8W9V0U1T2"})
    type: str = Field (..., max_length=255, json_schema_extra={"example": "info"})
    data: Dict[str, object] = Field (..., json_schema_extra={"example": {"title": "Welcome", "body": "Welcome to our platform"}})
