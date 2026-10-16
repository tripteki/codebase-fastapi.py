from datetime import datetime
from typing_extensions import Self
from pydantic import BaseModel, Field
from src.v1.api.acl.support.system_permission_guard import SystemPermissionGuard
from src.v1.api.user.databases.models.acl_model import Permission

class PermissionTransformerDto (BaseModel):
    """
    PermissionTransformerDto (BaseModel)

    Attributes:
        id (str)
        name (str)
        guard_name (str)
        is_protected (bool)
        created_at (datetime)
        updated_at (datetime)
    """
    id: str = Field (..., json_schema_extra={"example": "string"})
    name: str = Field (..., json_schema_extra={"example": "user.view"})
    guard_name: str = Field (..., json_schema_extra={"example": "web"})
    is_protected: bool = Field (..., json_schema_extra={"example": True})
    created_at: datetime = Field (..., json_schema_extra={"example": "string"})
    updated_at: datetime = Field (..., json_schema_extra={"example": "string"})

    @staticmethod
    def fromPermission (permission: Permission) -> Self:
        """
        Args:
            permission (Permission)
        Returns:
            PermissionTransformerDto
        """
        return PermissionTransformerDto (
            id=permission.id,
            name=permission.name,
            guard_name=permission.guard_name,
            is_protected=SystemPermissionGuard.isSystem (permission.name),
            created_at=permission.created_at,
            updated_at=permission.updated_at,
        )
