from sqlmodel import Session, select
from ulid import ULID
from src.app.bases.app_database import AppDatabase
from src.v1.api.user.databases.models.acl_model import ModelHasRole, Permission, Role, RoleHasPermission
from src.v1.api.user.databases.models.user_model import User

GUARD_NAME = "web"
USER_MODEL_TYPE = "User"

ROLE_PERMISSIONS = {
    "superadmin": [
        "user.view",
        "user.create",
        "user.update",
        "user.delete",
        "user.restore",
        "user.import",
        "user.export",
    ],
    "admin": [
        "user.view",
        "user.create",
        "user.update",
        "user.delete",
        "user.restore",
        "user.import",
        "user.export",
    ],
    "speaker": ["user.view"],
    "delegate": ["user.view"],
    "exhibitor": ["user.view"],
    "sponsor": ["user.view"],
    "visitor": ["user.view"],
}

ROLES = list (ROLE_PERMISSIONS.keys ())

class UserAclSeeder:
    """
    UserAclSeeder
    """
    @staticmethod
    def run () -> None:
        session = Session (AppDatabase.databasePostgresql ())
        try:
            permissionMap = UserAclSeeder._seedPermissions (session)
            roleMap = UserAclSeeder._seedRoles (session)
            UserAclSeeder._seedRolePermissions (session, permissionMap, roleMap)
            UserAclSeeder._assignSuperuserRole (session, roleMap)
            session.commit ()
        except Exception:
            session.rollback ()
            raise
        finally:
            session.close ()

    @staticmethod
    def _seedPermissions (session: Session) -> dict[str, Permission]:
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
    def _seedRolePermissions (
        session: Session,
        permissionMap: dict[str, Permission],
        roleMap: dict[str, Role],
    ) -> None:
        for roleName, permissionNames in ROLE_PERMISSIONS.items ():
            role = roleMap[roleName]

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
    def _assignSuperuserRole (session: Session, roleMap: dict[str, Role]) -> None:
        user = session.exec (
            select (User).where (User.name == "superuser", User.deleted_at == None)
        ).first ()

        if user is None:
            return

        role = roleMap["superadmin"]
        exists = session.exec (
            select (ModelHasRole).where (
                ModelHasRole.role_id == role.id,
                ModelHasRole.model_type == USER_MODEL_TYPE,
                ModelHasRole.model_id == user.id,
            )
        ).first ()

        if exists is None:
            session.add (ModelHasRole (
                role_id=role.id,
                model_type=USER_MODEL_TYPE,
                model_id=user.id,
            ))
