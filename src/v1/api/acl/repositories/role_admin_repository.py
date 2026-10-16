from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy import func
from sqlmodel import Session, col, select
from ulid import ULID
from src.app.bases.app_database import AppDatabase
from src.app.repositories.app_repository import OffsetPagination, OffsetPaginationType
from src.v1.api.acl.dtos.role_transformer_dto import RoleTransformerDto
from src.v1.api.user.databases.models.acl_model import (
    ModelHasRole,
    Permission,
    Role,
    RoleHasPermission,
)

SORTABLE_FIELDS = ("name", "guard_name", "created_at", "updated_at")

class RoleAdminRepository:
    """
    RoleAdminRepository
    """

    @staticmethod
    def getSession () -> Session:
        """
        Returns:
            Session
        """
        return Session (AppDatabase.databasePostgresql ())

    @staticmethod
    def _normalizeFilters (filters: Optional[List[Any]]) -> Dict[str, str]:
        """
        Args:
            filters (Optional[List[Any]])
        Returns:
            Dict[str, str]
        """
        normalized: Dict[str, str] = {}
        for item in filters or []:
            if isinstance (item, dict):
                field = str (item.get ("field") or "").strip ()
                search = str (item.get ("search") or "").strip ()
            else:
                field = str (getattr (item, "field", "") or "").strip ()
                search = str (getattr (item, "search", "") or "").strip ()
            if field and search:
                normalized[field] = search
        return normalized

    @staticmethod
    def _normalizeOrders (orders: Optional[List[Any]]) -> List[tuple[str, str]]:
        """
        Args:
            orders (Optional[List[Any]])
        Returns:
            List[tuple[str, str]]
        """
        normalized: List[tuple[str, str]] = []
        for item in orders or []:
            if isinstance (item, dict):
                field = str (item.get ("field") or "").strip ()
                direction = str (item.get ("direction") or "asc").strip ().lower ()
            else:
                field = str (getattr (item, "field", "") or "").strip ()
                direction = str (getattr (item, "direction", "asc") or "asc").strip ().lower ()
            if field:
                normalized.append ((field, "desc" if direction == "desc" else "asc"))
        return normalized or [("created_at", "desc")]

    @classmethod
    def _conditions (cls, filters: Optional[List[Any]]) -> List[Any]:
        """
        Args:
            filters (Optional[List[Any]])
        Returns:
            List[Any]
        """
        filterMap = cls._normalizeFilters (filters)
        conditions: List[Any] = []

        q = filterMap.get ("q") or filterMap.get ("search")
        if q:
            conditions.append (col (Role.name).ilike (f"%{q}%"))

        guardName = filterMap.get ("guard_name")
        if guardName:
            conditions.append (Role.guard_name == guardName)

        return conditions

    @classmethod
    def _orderBy (cls, orders: Optional[List[Any]]) -> List[Any]:
        """
        Args:
            orders (Optional[List[Any]])
        Returns:
            List[Any]
        """
        columns: List[Any] = []
        for field, direction in cls._normalizeOrders (orders):
            if field not in SORTABLE_FIELDS:
                continue
            column = getattr (Role, field)
            columns.append (column.desc () if direction == "desc" else column.asc ())
        return columns

    def _permissionsForRoles (
        self,
        session: Session,
        roleIds: List[str],
    ) -> Dict[str, List[Permission]]:
        """
        Args:
            session (Session)
            roleIds (List[str])
        Returns:
            Dict[str, List[Permission]]
        """
        if not roleIds:
            return {}

        rows = session.exec (
            select (RoleHasPermission.role_id, Permission)
            .join (Permission, Permission.id == RoleHasPermission.permission_id)
            .where (RoleHasPermission.role_id.in_ (roleIds))
        ).all ()

        mapped: Dict[str, List[Permission]] = {}
        for roleId, permission in rows:
            mapped.setdefault (roleId, []).append (permission)
        return mapped

    def _usersCountForRoles (
        self,
        session: Session,
        roleIds: List[str],
    ) -> Dict[str, int]:
        """
        Args:
            session (Session)
            roleIds (List[str])
        Returns:
            Dict[str, int]
        """
        if not roleIds:
            return {}

        rows = session.exec (
            select (ModelHasRole.role_id, func.count ())
            .where (ModelHasRole.role_id.in_ (roleIds))
            .group_by (ModelHasRole.role_id)
        ).all ()
        return {roleId: count for roleId, count in rows}

    async def countUsers (self, roleId: str) -> int:
        """
        Args:
            roleId (str)
        Returns:
            int
        """
        session = self.getSession ()
        try:
            return self._usersCountForRoles (session, [roleId]).get (roleId, 0)
        finally:
            session.close ()

    async def allOffset (
        self,
        orders: List[Any] = None,
        filters: List[Any] = None,
        page: OffsetPaginationType = None,
    ) -> OffsetPagination[RoleTransformerDto]:
        """
        Args:
            orders (List[Any])
            filters (List[Any])
            page (OffsetPaginationType)
        Returns:
            OffsetPagination[RoleTransformerDto]
        """
        page = page or OffsetPaginationType (currentPage=1, limitPage=10)
        conditions = self._conditions (filters)

        session = self.getSession ()
        try:
            statement = select (Role).where (*conditions).order_by (*self._orderBy (orders))
            countStatement = select (func.count ()).select_from (Role).where (*conditions)

            total = session.exec (countStatement).one ()
            offset = (page.currentPage - 1) * page.limitPage
            roles = session.exec (statement.offset (offset).limit (page.limitPage)).all ()
            permissionsMap = self._permissionsForRoles (session, [role.id for role in roles])
            usersCountMap = self._usersCountForRoles (session, [role.id for role in roles])

            perPage = page.limitPage
            currentPage = page.currentPage
            lastPage = (total + perPage - 1) // perPage if total > 0 else 1

            return OffsetPagination (
                total=int (total),
                totalPage=lastPage,
                perPage=perPage,
                currentPage=currentPage,
                nextPage=currentPage + 1 if currentPage < lastPage else None,
                previousPage=currentPage - 1 if currentPage > 1 else None,
                firstPage=1,
                lastPage=lastPage,
                data=[
                    RoleTransformerDto.fromRole (
                        role,
                        permissionsMap.get (role.id, []),
                        usersCountMap.get (role.id, 0),
                    )
                    for role in roles
                ],
            )
        finally:
            session.close ()

    async def allFiltered (
        self,
        orders: List[Any] = None,
        filters: List[Any] = None,
    ) -> List[Role]:
        """
        Args:
            orders (List[Any])
            filters (List[Any])
        Returns:
            List[Role]
        """
        session = self.getSession ()
        try:
            return list (
                session.exec (
                    select (Role).where (*self._conditions (filters)).order_by (*self._orderBy (orders))
                ).all ()
            )
        finally:
            session.close ()

    async def findById (self, id: str) -> Optional[Role]:
        """
        Args:
            id (str)
        Returns:
            Optional[Role]
        """
        session = self.getSession ()
        try:
            return session.exec (select (Role).where (Role.id == id)).first ()
        finally:
            session.close ()

    async def findByNameGuard (self, name: str, guardName: str) -> Optional[Role]:
        """
        Args:
            name (str)
            guardName (str)
        Returns:
            Optional[Role]
        """
        session = self.getSession ()
        try:
            return session.exec (
                select (Role).where (
                    Role.name == name,
                    Role.guard_name == guardName,
                )
            ).first ()
        finally:
            session.close ()

    async def getPermissions (self, roleId: str) -> List[Permission]:
        """
        Args:
            roleId (str)
        Returns:
            List[Permission]
        """
        session = self.getSession ()
        try:
            return list (
                session.exec (
                    select (Permission)
                    .join (RoleHasPermission, RoleHasPermission.permission_id == Permission.id)
                    .where (RoleHasPermission.role_id == roleId)
                ).all ()
            )
        finally:
            session.close ()

    async def create (self, name: str, guardName: str, permissionIds: List[str]) -> Role:
        """
        Args:
            name (str)
            guardName (str)
            permissionIds (List[str])
        Returns:
            Role
        """
        session = self.getSession ()
        try:
            role = Role (
                id=str (ULID ()),
                name=name,
                guard_name=guardName,
            )
            session.add (role)
            session.flush ()

            if permissionIds:
                permissions = session.exec (
                    select (Permission).where (Permission.id.in_ (permissionIds))
                ).all ()
                for permission in permissions:
                    session.add (RoleHasPermission (
                        role_id=role.id,
                        permission_id=permission.id,
                    ))

            session.commit ()
            session.refresh (role)
            return role
        except Exception:
            session.rollback ()
            raise
        finally:
            session.close ()

    async def update (
        self,
        role: Role,
        *,
        name: Optional[str] = None,
        guardName: Optional[str] = None,
        permissionIds: Optional[List[str]] = None,
    ) -> Role:
        """
        Args:
            role (Role)
            name (Optional[str])
            guardName (Optional[str])
            permissionIds (Optional[List[str]])
        Returns:
            Role
        """
        session = self.getSession ()
        try:
            attached = session.exec (select (Role).where (Role.id == role.id)).first ()
            if attached is None:
                return role

            if name is not None:
                attached.name = name
            if guardName is not None:
                attached.guard_name = guardName
            attached.updated_at = datetime.utcnow ()
            session.add (attached)

            if permissionIds is not None:
                existing = session.exec (
                    select (RoleHasPermission).where (RoleHasPermission.role_id == attached.id)
                ).all ()
                for link in existing:
                    session.delete (link)
                session.flush ()

                if permissionIds:
                    permissions = session.exec (
                        select (Permission).where (Permission.id.in_ (permissionIds))
                    ).all ()
                    for permission in permissions:
                        session.add (RoleHasPermission (
                            role_id=attached.id,
                            permission_id=permission.id,
                        ))

            session.commit ()
            session.refresh (attached)
            return attached
        except Exception:
            session.rollback ()
            raise
        finally:
            session.close ()

    async def delete (self, role: Role) -> None:
        """
        Args:
            role (Role)
        Returns:
            None
        """
        session = self.getSession ()
        try:
            attached = session.exec (select (Role).where (Role.id == role.id)).first ()
            if attached is None:
                return

            permissionLinks = session.exec (
                select (RoleHasPermission).where (RoleHasPermission.role_id == attached.id)
            ).all ()
            for link in permissionLinks:
                session.delete (link)

            userLinks = session.exec (
                select (ModelHasRole).where (ModelHasRole.role_id == attached.id)
            ).all ()
            for link in userLinks:
                session.delete (link)

            session.delete (attached)
            session.commit ()
        except Exception:
            session.rollback ()
            raise
        finally:
            session.close ()
