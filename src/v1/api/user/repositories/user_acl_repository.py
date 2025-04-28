from typing import List, Tuple
from sqlmodel import Session, select
from src.app.bases.app_database import AppDatabase
from src.v1.api.user.databases.models.acl_model import ModelHasRole, Permission, Role, RoleHasPermission

USER_MODEL_TYPE = "User"

class UserAclRepository:
    """
    UserAclRepository
    """
    @staticmethod
    def getSession () -> Session:
        """
        Returns:
            Session
        """
        return Session (AppDatabase.databasePostgresql ())

    @staticmethod
    async def getUserAccesses (userId: str) -> Tuple[List[str], List[str]]:
        """
        Args:
            userId (str)
        Returns:
            Tuple[List[str], List[str]]
        """
        session = UserAclRepository.getSession ()
        try:
            roleLinks = session.exec (
                select (ModelHasRole).where (
                    ModelHasRole.model_id == userId,
                    ModelHasRole.model_type == USER_MODEL_TYPE,
                )
            ).all ()

            roleIds = [link.role_id for link in roleLinks]
            if not roleIds:
                return [], []

            roles = session.exec (
                select (Role).where (Role.id.in_ (roleIds))
            ).all ()
            roleNames = sorted ({role.name for role in roles})

            permissionLinks = session.exec (
                select (RoleHasPermission).where (RoleHasPermission.role_id.in_ (roleIds))
            ).all ()
            permissionIds = [link.permission_id for link in permissionLinks]
            if not permissionIds:
                return [], roleNames

            permissions = session.exec (
                select (Permission).where (Permission.id.in_ (permissionIds))
            ).all ()

            return sorted ({permission.name for permission in permissions}), roleNames
        finally:
            session.close ()
