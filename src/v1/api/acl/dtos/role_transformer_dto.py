from datetime import datetime
from typing import List, Optional
from typing_extensions import Self
from pydantic import BaseModel, Field
from src.v1.api.acl.support.system_role_guard import SystemRoleGuard
from src.v1.api.user.dtos.user_role_enum import UserRoleEnum
from src.v1.api.user.databases.models.acl_model import Permission, Role

class RolePermissionTransformerDto (BaseModel):
    """
    RolePermissionTransformerDto (BaseModel)

    Attributes:
        id (str)
        name (str)
        guard_name (str)
    """
    id: str = Field (..., json_schema_extra={"example": "string"})
    name: str = Field (..., json_schema_extra={"example": "user.view"})
    guard_name: str = Field (..., json_schema_extra={"example": "web"})

class RoleTransformerDto (BaseModel):
    """
    RoleTransformerDto (BaseModel)

    Attributes:
        id (str)
        name (str)
        guard_name (str)
        permissions (List[RolePermissionTransformerDto])
        is_protected (bool)
        users_count (int)
        created_at (datetime)
        updated_at (datetime)
    """
    id: str = Field (..., json_schema_extra={"example": "string"})
    name: str = Field (..., json_schema_extra={"example": UserRoleEnum.Admin.value})
    guard_name: str = Field (..., json_schema_extra={"example": "web"})
    permissions: List[RolePermissionTransformerDto] = Field (default_factory=list)
    is_protected: bool = Field (..., json_schema_extra={"example": True})
    users_count: int = Field (0, json_schema_extra={"example": 0})
    created_at: datetime = Field (..., json_schema_extra={"example": "string"})
    updated_at: datetime = Field (..., json_schema_extra={"example": "string"})

    @staticmethod
    def fromRole (role: Role, permissions: Optional[List[Permission]] = None, usersCount: int = 0) -> Self:
        """
        Args:
            role (Role)
            permissions (Optional[List[Permission]])
            usersCount (int)
        Returns:
            RoleTransformerDto
        """
        perms = permissions or []
        return RoleTransformerDto (
            id=role.id,
            name=role.name,
            guard_name=role.guard_name,
            permissions=[
                RolePermissionTransformerDto (
                    id=permission.id,
                    name=permission.name,
                    guard_name=permission.guard_name,
                )
                for permission in sorted (perms, key=lambda item: item.name)
            ],
            is_protected=SystemRoleGuard.isSystem (role.name),
            users_count=usersCount,
            created_at=role.created_at,
            updated_at=role.updated_at,
        )
