from sqlmodel import Session, select
from ulid import ULID
from src.app.bases.app_database import AppDatabase
from src.v1.api.user.databases.models.acl_model import ModelHasRole, Permission, Role, RoleHasPermission
from src.v1.api.user.databases.models.user_model import User
from src.app.configs.app_config import AppConfig
from src.v1.api.user.dtos.user_enum import UserEnum
from src.v1.api.user.dtos.user_role_enum import UserRoleEnum

GUARD_NAME = "web"
USER_MODEL_TYPE = "User"

def superuser_email () -> str:
    """
    Returns:
        str
    """
    return f"{UserEnum.Superuser.value}@{AppConfig.config ().email_server ()}"

USER_PERMISSIONS = [
    "user.view",
    "user.create",
    "user.update",
    "user.delete",
    "user.restore",
    "user.import",
    "user.export",
]

ROLE_ACL_PERMISSIONS = [
    "role.view",
    "role.create",
    "role.update",
    "role.delete",
    "role.import",
    "role.export",
]

PERMISSION_ACL_PERMISSIONS = [
    "permission.view",
    "permission.create",
    "permission.update",
    "permission.delete",
    "permission.import",
    "permission.export",
]

ACTIVITY_PERMISSIONS = [
    "activity.view",
]

NOTIFICATION_PERMISSIONS = [
    "notification.view",
    "notification.delete",
]

SUPERADMIN_PERMISSIONS = (
    USER_PERMISSIONS
    + ROLE_ACL_PERMISSIONS
    + PERMISSION_ACL_PERMISSIONS
    + ACTIVITY_PERMISSIONS
    + NOTIFICATION_PERMISSIONS
)

ADMIN_PERMISSIONS = (
    USER_PERMISSIONS
    + ACTIVITY_PERMISSIONS
    + NOTIFICATION_PERMISSIONS
)

USER_ROLE_PERMISSIONS = (
    ACTIVITY_PERMISSIONS
    + NOTIFICATION_PERMISSIONS
)

ROLE_PERMISSIONS = {
    UserRoleEnum.Superadmin: SUPERADMIN_PERMISSIONS,
    UserRoleEnum.Admin: ADMIN_PERMISSIONS,
    UserRoleEnum.User: USER_ROLE_PERMISSIONS,
}

ROLES = list (UserRoleEnum.values ())

class UserAclSeeder:
    """
    UserAclSeeder
    """
    @staticmethod
    def run () -> None:
        """
        Returns:
            None
        """
        session = Session (AppDatabase.databasePostgresql ())
        try:
            permissionMap = UserAclSeeder._seedPermissions (session)
            roleMap = UserAclSeeder._seedRoles (session)
            UserAclSeeder._pruneUnknownRoles (session, roleMap)
            UserAclSeeder._seedRolePermissions (session, permissionMap, roleMap)
            UserAclSeeder._assignSuperadminRole (session, roleMap)
            session.commit ()
        except Exception:
            session.rollback ()
            raise
        finally:
            session.close ()

    @staticmethod
    def _seedPermissions (session: Session) -> dict[str, Permission]:
        """
        Args:
            session (Session)
        Returns:
            dict[str, Permission]
        """
        permissionNames = sorted ({
            permission
            for permissions in ROLE_PERMISSIONS.values ()
            for permission in permissions
        })
        permissionMap: dict[str, Permission] = {}

        for name in permissionNames:
            permission = session.exec (
                select (Permission).where (
                    Permission.name == name,
                    Permission.guard_name == GUARD_NAME,
                )
            ).first ()

            if permission is None:
                permission = Permission (
                    id=str (ULID ()),
                    name=name,
                    guard_name=GUARD_NAME,
                )
                session.add (permission)

            permissionMap[name] = permission

        session.flush ()
        return permissionMap

    @staticmethod
    def _seedRoles (session: Session) -> dict[str, Role]:
        """
        Args:
            session (Session)
        Returns:
            dict[str, Role]
        """
        roleMap: dict[str, Role] = {}

        for name in ROLES:
            role = session.exec (
                select (Role).where (
                    Role.name == name,
                    Role.guard_name == GUARD_NAME,
                )
            ).first ()

            if role is None:
                role = Role (
                    id=str (ULID ()),
                    name=name,
                    guard_name=GUARD_NAME,
                )
                session.add (role)

            roleMap[name] = role

        session.flush ()
        return roleMap

    @staticmethod
    def _pruneUnknownRoles (session: Session, roleMap: dict[str, Role]) -> None:
        """
        Args:
            session (Session)
            roleMap (dict[str, Role])
        Returns:
            None
        """
        keepIds = {role.id for role in roleMap.values ()}

        for role in session.exec (select (Role)).all ():
            if role.id in keepIds:
                continue

            for link in session.exec (
                select (RoleHasPermission).where (RoleHasPermission.role_id == role.id)
            ).all ():
                session.delete (link)

            for link in session.exec (
                select (ModelHasRole).where (ModelHasRole.role_id == role.id)
            ).all ():
                session.delete (link)

            session.delete (role)

        session.flush ()

    @staticmethod
    def _seedRolePermissions (
        session: Session,
        permissionMap: dict[str, Permission],
        roleMap: dict[str, Role],
    ) -> None:
        """
        Args:
            session (Session)
            permissionMap (dict[str, Permission])
            roleMap (dict[str, Role])
        Returns:
            None
        """
        for roleName, permissionNames in ROLE_PERMISSIONS.items ():
            role = roleMap[roleName.value]
            keepPermissionIds = {
                permissionMap[permissionName].id
                for permissionName in permissionNames
            }

            for link in session.exec (
                select (RoleHasPermission).where (RoleHasPermission.role_id == role.id)
            ).all ():
                if link.permission_id not in keepPermissionIds:
                    session.delete (link)

            for permissionName in permissionNames:
                permission = permissionMap[permissionName]
                exists = session.exec (
                    select (RoleHasPermission).where (
                        RoleHasPermission.role_id == role.id,
                        RoleHasPermission.permission_id == permission.id,
                    )
                ).first ()

                if exists is None:
                    session.add (RoleHasPermission (
                        role_id=role.id,
                        permission_id=permission.id,
                    ))

        session.flush ()

    @staticmethod
    def _assignSuperadminRole (session: Session, roleMap: dict[str, Role]) -> None:
        """
        Args:
            session (Session)
            roleMap (dict[str, Role])
        Returns:
            None
        """
        user = session.exec (
            select (User).where (User.email == superuser_email (), User.deleted_at == None)
        ).first ()

        if user is None:
            return

        role = roleMap[UserRoleEnum.Superadmin.value]
        existingLinks = session.exec (
            select (ModelHasRole).where (
                ModelHasRole.model_type == USER_MODEL_TYPE,
                ModelHasRole.model_id == user.id,
            )
        ).all ()

        for link in existingLinks:
            if link.role_id != role.id:
                session.delete (link)

        hasOwner = any (link.role_id == role.id for link in existingLinks)
        if not hasOwner:
            session.add (ModelHasRole (
                role_id=role.id,
                model_type=USER_MODEL_TYPE,
                model_id=user.id,
            ))

