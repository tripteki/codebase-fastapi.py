from datetime import datetime
from sqlmodel import SQLModel, Field
from ulid import ULID

class Permission (SQLModel, table=True):
    """
    Permission (SQLModel)
    """
    __tablename__ = "permissions"
    id: str = Field (default_factory=lambda: str (ULID ()), primary_key=True)
    name: str = Field (index=True)
    guard_name: str = Field (default="web")
    created_at: datetime = Field (default_factory=datetime.utcnow)
    updated_at: datetime = Field (default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})

class Role (SQLModel, table=True):
    """
    Role (SQLModel)
    """
    __tablename__ = "roles"
    id: str = Field (default_factory=lambda: str (ULID ()), primary_key=True)
    name: str = Field (index=True)
    guard_name: str = Field (default="web")
    created_at: datetime = Field (default_factory=datetime.utcnow)
    updated_at: datetime = Field (default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})

class RoleHasPermission (SQLModel, table=True):
    """
    RoleHasPermission (SQLModel)
    """
    __tablename__ = "role_has_permissions"
    permission_id: str = Field (foreign_key="permissions.id", primary_key=True)
    role_id: str = Field (foreign_key="roles.id", primary_key=True)

class ModelHasRole (SQLModel, table=True):
    """
    ModelHasRole (SQLModel)
    """
    __tablename__ = "model_has_roles"
    role_id: str = Field (foreign_key="roles.id", primary_key=True)
    model_type: str = Field (primary_key=True)
    model_id: str = Field (primary_key=True)
