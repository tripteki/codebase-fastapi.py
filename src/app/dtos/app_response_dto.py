from typing import Optional, Generic, TypeVar
from pydantic import BaseModel, Field
from src.app.dtos.app_dto import Status, Message

T = TypeVar ("T")

class AppResponseDto (BaseModel, Generic[T]):
    """
    AppResponseDto (BaseModel, Generic)

    Attributes:
        status (int)
        message (str)
        data (Optional[T])
    """
    status: int = Field (..., json_schema_extra={"example": 0})
    message: str = Field (..., json_schema_extra={"example": "string"})
    data: Optional[T] = None

class AppSuccessResponseDto (BaseModel, Generic[T]):
    """
    AppSuccessResponseDto (BaseModel, Generic)

    Attributes:
        status (int)
        message (str)
        data (Optional[T])
    """
    status: int = Field (default=Status.OK, json_schema_extra={"example": 0})
    message: str = Field (default=Message.OK, json_schema_extra={"example": "string"})
    data: Optional[T] = None

class AppErrorResponseDto (BaseModel):
    """
    AppErrorResponseDto (BaseModel)

    Attributes:
        status (int)
        message (str)
        data (Optional[object])
    """
    status: int = Field (default=Status.UNVALIDATED, json_schema_extra={"example": 0})
    message: str = Field (default=Message.UNVALIDATED, json_schema_extra={"example": "string"})
    data: Optional[object] = None
