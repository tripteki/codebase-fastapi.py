import asyncio
import logging
from typing import Dict, List, Optional, Set, Tuple
from src.app.bases.app_realtime import emitToUser
from src.v1.api.user.dtos.user_role_enum import UserRoleEnum
from src.v1.api.user.repositories.user_acl_repository import UserAclRepository

logger = logging.getLogger (__name__)

ADMIN_REFRESH_EVENT = "v1.admin.refresh"

SCOPE_PERMISSIONS: Dict[str, Tuple[str, ...]] = {
    "users": ("user.view",),
    "roles": ("role.view",),
    "permissions": ("permission.view",),
    "activities": ("activity.view",),
}

SUBJECT_SCOPES: Dict[str, Tuple[str, ...]] = {
    "User": ("users",),
    "Role": ("roles",),
    "Permission": ("permissions",),
    "Setting": (),
}

_pending: Set[asyncio.Task] = set ()

class AdminRefreshBroadcaster:
    """
    AdminRefreshBroadcaster
    """

    @staticmethod
    async def broadcast (scopes: List[str], exceptUserId: Optional[str] = None) -> None:
        """
        Args:
            scopes (List[str])
            exceptUserId (Optional[str])
        Returns:
            None
        """
        try:
            permissionNames = {"activity.view"}
            for scope in scopes:
                permissionNames.update (SCOPE_PERMISSIONS.get (scope, ()))

            userIds = await UserAclRepository.findUserIdsByPermissionNames (
                sorted (permissionNames),
                [UserRoleEnum.Superadmin.value],
            )
            for userId in userIds:
                if userId == exceptUserId:
                    continue
                await emitToUser (userId, ADMIN_REFRESH_EVENT, {
                    "userId": userId,
                    "scopes": list (scopes),
                })
        except Exception:
            logger.warning ("admin refresh broadcast failed scopes=%s", scopes, exc_info=True)

    @staticmethod
    def schedule (scopes: List[str], exceptUserId: Optional[str] = None) -> None:
        """
        Args:
            scopes (List[str])
            exceptUserId (Optional[str])
        Returns:
            None
        """
        try:
            loop = asyncio.get_running_loop ()
        except RuntimeError:
            return

        task = loop.create_task (AdminRefreshBroadcaster.broadcast (scopes, exceptUserId))
        _pending.add (task)
        task.add_done_callback (_pending.discard)

    @staticmethod
    def scheduleForSubject (subjectType: Optional[str], causerId: Optional[str]) -> None:
        """
        Args:
            subjectType (Optional[str])
            causerId (Optional[str])
        Returns:
            None
        """
        if subjectType not in SUBJECT_SCOPES:
            return

        AdminRefreshBroadcaster.schedule (list (SUBJECT_SCOPES[subjectType]), causerId)
