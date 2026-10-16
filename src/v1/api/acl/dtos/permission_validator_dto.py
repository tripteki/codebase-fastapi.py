from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, Field

GuardName = Literal["web", "api"]

class PermissionCreateValidatorDto (BaseModel):
    """
    PermissionCreateValidatorDto (BaseModel)

    Attributes:
        name (str)
        guard_name (GuardName)
    """
    model_config = ConfigDict (extra="forbid", str_strip_whitespace=True)

    name: str = Field (..., min_length=1, max_length=255, json_schema_extra={"example": "report.view"})
    guard_name: GuardName = Field (default="web", json_schema_extra={"example": "web"})

class PermissionUpdateValidatorDto (BaseModel):
    """
    PermissionUpdateValidatorDto (BaseModel)

    Attributes:
        name (Optional[str])
        guard_name (Optional[GuardName])
    """
    model_config = ConfigDict (extra="forbid", str_strip_whitespace=True)

    name: Optional[str] = Field (default=None, min_length=1, max_length=255, json_schema_extra={"example": "report.view"})
    guard_name: Optional[GuardName] = Field (default=None, json_schema_extra={"example": "web"})
