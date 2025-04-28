from typing import Optional, Generic, TypeVar, Any
from pydantic import BaseModel, Field
from src.app.dtos.app_dto import Status, Message

T = TypeVar ("T")

class AppResponseDto (BaseModel, Generic[T]):
    """
    AppResponseDto
    """
    status: int = Field (..., json_schema_extra={"example": 0})
    message: str = Field (..., json_schema_extra={"example": "string"})
    data: Optional[T] = None

class AppSuccessResponseDto (BaseModel, Generic[T]):
    """
    AppSuccessResponseDto
    """
    status: int = Field (default=Status.OK, json_schema_extra={"example": 0})
    message: str = Field (default=Message.OK, json_schema_extra={"example": "string"})
    data: Optional[T] = None

class AppErrorResponseDto (BaseModel):
    """
    AppErrorResponseDto
    """
    status: int = Field (default=Status.UNVALIDATED, json_schema_extra={"example": 0})
    message: str = Field (default=Message.UNVALIDATED, json_schema_extra={"example": "string"})
    data: Optional[Any] = None
