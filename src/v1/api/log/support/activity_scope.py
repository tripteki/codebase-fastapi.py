from typing import Optional
from sqlalchemy import ColumnElement, and_, or_
from src.v1.api.log.databases.models.activity_model import Activity
from src.v1.api.user.dtos.user_role_enum import UserRoleEnum
from src.v1.api.user.repositories.user_acl_repository import UserAclRepository

USER_SUBJECT_TYPE = "User"

class ActivityScope:
    """
    ActivityScope

    Roles outside UserRoleEnum.activityReaders only see activities they caused or that concern their own account.
    """

    @staticmethod
    async def ownerIdFor (userId: str) -> Optional[str]:
        """
        Args:
            userId (str)
        Returns:
            Optional[str]
        """
        _, roles = await UserAclRepository.getUserAccesses (userId)
        if any (role in UserRoleEnum.activityReaders () for role in roles):
            return None
        return userId

    @staticmethod
    def condition (ownerId: str) -> ColumnElement:
        """
        Args:
            ownerId (str)
        Returns:
            ColumnElement
        """
        return or_ (
            Activity.causer_id == ownerId,
            and_ (
                Activity.subject_type == USER_SUBJECT_TYPE,
                Activity.subject_id == ownerId,
            ),
        )
