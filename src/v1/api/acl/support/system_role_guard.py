from fastapi import HTTPException, status
from src.app.bases.app_i18n import AppI18n
from src.v1.api.user.dtos.user_role_enum import UserRoleEnum

class SystemRoleGuard:
    """
    SystemRoleGuard
    """

    @staticmethod
    def isSystem (name: str) -> bool:
        """
        Args:
            name (str)
        Returns:
            bool
        """
        return name in UserRoleEnum.values ()

    @staticmethod
    def assertCreatableName (name: str) -> None:
        """
        Args:
            name (str)
        Returns:
            None
        """
        if SystemRoleGuard.isSystem (name):
            i18n = AppI18n.i18n ()
            raise HTTPException (
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=i18n.t ("_v1_acl.role.system_role_name_reserved"),
            )

    @staticmethod
    def assertMutableName (name: str) -> None:
        """
        Args:
            name (str)
        Returns:
            None
        """
        if SystemRoleGuard.isSystem (name):
            i18n = AppI18n.i18n ()
            raise HTTPException (
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=i18n.t ("_v1_acl.role.system_role_locked"),
            )
