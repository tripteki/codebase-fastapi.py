from typing import Set
from fastapi import HTTPException, status
from src.app.bases.app_i18n import AppI18n

SYSTEM_PERMISSION_NAMES: Set[str] = {
    "user.view",
    "user.create",
    "user.update",
    "user.delete",
    "user.restore",
    "user.import",
    "user.export",
    "role.view",
    "role.create",
    "role.update",
    "role.delete",
    "role.import",
    "role.export",
    "permission.view",
    "permission.create",
    "permission.update",
    "permission.delete",
    "permission.import",
    "permission.export",
    "activity.view",
    "notification.view",
    "notification.delete",
}

class SystemPermissionGuard:
    """
    SystemPermissionGuard
    """

    @staticmethod
    def isSystem (name: str) -> bool:
        """
        Args:
            name (str)
        Returns:
            bool
        """
        return name in SYSTEM_PERMISSION_NAMES

    @staticmethod
    def assertMutable (name: str) -> None:
        """
        Args:
            name (str)
        Returns:
            None
        """
        if SystemPermissionGuard.isSystem (name):
            i18n = AppI18n.i18n ()
            raise HTTPException (
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=i18n.t ("_v1_acl.permission.system_permission_locked"),
            )
