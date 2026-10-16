from typing import List, Optional, Tuple
from sqlmodel import Session, col, select
from ulid import ULID
from src.app.bases.app_database import AppDatabase
from src.v1.api.user.databases.models.acl_model import ModelHasRole, Permission, Role, RoleHasPermission
from src.v1.api.user.databases.models.user_model import User

USER_MODEL_TYPE = "User"
GUARD_NAME = "web"

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

    @staticmethod
    def assignSingleRole (userId: str, roleName: str) -> None:
        """
        Args:
            userId (str)
            roleName (str)
        Returns:
            None
        """
        session = UserAclRepository.getSession ()
        try:
            role = session.exec (
                select (Role).where (
                    Role.name == roleName,
                    Role.guard_name == GUARD_NAME,
                )
            ).first ()
            if role is None:
                raise LookupError (roleName)

            existingLinks = session.exec (
                select (ModelHasRole).where (
                    ModelHasRole.model_id == userId,
                    ModelHasRole.model_type == USER_MODEL_TYPE,
                )
            ).all ()

            for link in existingLinks:
                if link.role_id != role.id:
                    session.delete (link)

            if not any (link.role_id == role.id for link in existingLinks):
                session.add (ModelHasRole (
                    role_id=role.id,
                    model_type=USER_MODEL_TYPE,
                    model_id=userId,
                ))

            session.commit ()
        except Exception:
            session.rollback ()
            raise
        finally:
            session.close ()

    @staticmethod
    async def getUserRole (userId: str) -> Optional[str]:
        """
        Args:
            userId (str)
        Returns:
            Optional[str]
        """
        _, roles = await UserAclRepository.getUserAccesses (userId)
        return roles[0] if roles else None

    @staticmethod
    async def findUserIdsByRoleNames (roleNames: List[str]) -> List[str]:
        """
        Args:
            roleNames (List[str])
        Returns:
            List[str]
        """
        if not roleNames:
            return []

        session = UserAclRepository.getSession ()
        try:
            roles = session.exec (
                select (Role).where (
                    col (Role.name).in_ (roleNames),
                    Role.guard_name == GUARD_NAME,
                )
            ).all ()
            roleIds = [role.id for role in roles]
            if not roleIds:
                return []

            links = session.exec (
                select (ModelHasRole).where (
                    col (ModelHasRole.role_id).in_ (roleIds),
                    ModelHasRole.model_type == USER_MODEL_TYPE,
                )
            ).all ()
            userIds = {link.model_id for link in links}
            if not userIds:
                return []

            users = session.exec (
                select (User).where (
                    col (User.id).in_ (list (userIds)),
                    User.deleted_at == None,
                )
            ).all ()
            return sorted ({user.id for user in users})
        finally:
            session.close ()

    @staticmethod
    async def findUserIdsByPermissionNames (permissionNames: List[str], extraRoleNames: List[str]) -> List[str]:
        """
        Args:
            permissionNames (List[str])
            extraRoleNames (List[str])
        Returns:
            List[str]
        """
        roleNames = set (extraRoleNames)
        if permissionNames:
            session = UserAclRepository.getSession ()
            try:
                rows = session.exec (
                    select (Role.name)
                    .join (RoleHasPermission, RoleHasPermission.role_id == Role.id)
                    .join (Permission, Permission.id == RoleHasPermission.permission_id)
                    .where (
                        col (Permission.name).in_ (permissionNames),
                        Role.guard_name == GUARD_NAME,
                    )
                ).all ()
                roleNames.update (rows)
            finally:
                session.close ()

        return await UserAclRepository.findUserIdsByRoleNames (sorted (roleNames))

    @staticmethod
    async def syncUserRole (userId: str, roleName: str) -> str:
        """
        Args:
            userId (str)
            roleName (str)
        Returns:
            str
        """
        session = UserAclRepository.getSession ()
        try:
            role = session.exec (
                select (Role).where (
                    Role.name == roleName,
                    Role.guard_name == GUARD_NAME,
                )
            ).first ()

            if role is None:
                role = Role (
                    id=str (ULID ()),
                    name=roleName,
                    guard_name=GUARD_NAME,
                )
                session.add (role)
                session.flush ()

            existingLinks = session.exec (
                select (ModelHasRole).where (
                    ModelHasRole.model_id == userId,
                    ModelHasRole.model_type == USER_MODEL_TYPE,
                )
            ).all ()

            keep = False
            for link in existingLinks:
                if link.role_id == role.id:
                    keep = True
                else:
                    session.delete (link)

            if not keep:
                session.add (ModelHasRole (
                    role_id=role.id,
                    model_type=USER_MODEL_TYPE,
                    model_id=userId,
                ))

            session.commit ()
            return roleName
        except Exception:
            session.rollback ()
            raise
        finally:
            session.close ()
