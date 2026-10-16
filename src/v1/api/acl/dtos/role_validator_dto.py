from typing import List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field

GuardName = Literal["web", "api"]

class RoleCreateValidatorDto (BaseModel):
    """
    RoleCreateValidatorDto (BaseModel)

    Attributes:
        name (str)
        guard_name (GuardName)
        permission_ids (List[str])
    """
    model_config = ConfigDict (extra="forbid", str_strip_whitespace=True)

    name: str = Field (..., min_length=1, max_length=255, json_schema_extra={"example": "analyst"})
    guard_name: GuardName = Field (default="web", json_schema_extra={"example": "web"})
    permission_ids: List[str] = Field (default_factory=list, json_schema_extra={"example": []})

class RoleUpdateValidatorDto (BaseModel):
    """
    RoleUpdateValidatorDto (BaseModel)

    Attributes:
        name (Optional[str])
        guard_name (Optional[GuardName])
        permission_ids (Optional[List[str]])
    """
    model_config = ConfigDict (extra="forbid", str_strip_whitespace=True)

    name: Optional[str] = Field (default=None, min_length=1, max_length=255, json_schema_extra={"example": "analyst"})
    guard_name: Optional[GuardName] = Field (default=None, json_schema_extra={"example": "web"})
    permission_ids: Optional[List[str]] = Field (default=None, json_schema_extra={"example": []})
