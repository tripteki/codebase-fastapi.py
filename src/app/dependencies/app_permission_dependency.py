from typing import Callable, Optional
from fastapi import Depends, HTTPException, status
from src.app.bases.app_i18n import AppI18n
from src.app.dependencies.app_auth_api_dependency import get_current_user
from src.v1.api.user.databases.models.user_model import User
from src.v1.api.user.dtos.user_role_enum import UserRoleEnum
from src.v1.api.user.repositories.user_acl_repository import UserAclRepository

def requirePermission (*permissions: str) -> Callable:
    """
    Args:
        *permissions (str)
    Returns:
        Callable
    """
    required = tuple (permissions)

    async def dependency (
        current_user: User = Depends (get_current_user),
    ) -> User:
        """
        Args:
            current_user (User)
        Returns:
            User
        """
        i18n = AppI18n.i18n ()
        userPermissions, roles = await UserAclRepository.getUserAccesses (current_user.id)

        if UserRoleEnum.Superadmin in roles:
            return current_user

        if required and any (name in userPermissions for name in required):
            return current_user

        raise HTTPException (
            status_code=status.HTTP_403_FORBIDDEN,
            detail=i18n.t ("_v1_user.auth.forbidden"),
        )

    return dependency
