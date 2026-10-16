from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy import func
from sqlmodel import Session, col, select
from ulid import ULID
from src.app.bases.app_database import AppDatabase
from src.app.repositories.app_repository import OffsetPagination, OffsetPaginationType
from src.v1.api.acl.dtos.permission_transformer_dto import PermissionTransformerDto
from src.v1.api.user.databases.models.acl_model import Permission, RoleHasPermission

SORTABLE_FIELDS = ("name", "guard_name", "created_at", "updated_at")

class PermissionAdminRepository:
    """
    PermissionAdminRepository
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
            conditions.append (col (Permission.name).ilike (f"%{q}%"))

        guardName = filterMap.get ("guard_name")
        if guardName:
            conditions.append (Permission.guard_name == guardName)

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
            column = getattr (Permission, field)
            columns.append (column.desc () if direction == "desc" else column.asc ())
        return columns

    async def allOffset (
        self,
        orders: List[Any] = None,
        filters: List[Any] = None,
        page: OffsetPaginationType = None,
    ) -> OffsetPagination[PermissionTransformerDto]:
        """
        Args:
            orders (List[Any])
            filters (List[Any])
            page (OffsetPaginationType)
        Returns:
            OffsetPagination[PermissionTransformerDto]
        """
        page = page or OffsetPaginationType (currentPage=1, limitPage=10)
        conditions = self._conditions (filters)

        session = self.getSession ()
        try:
            statement = select (Permission).where (*conditions).order_by (*self._orderBy (orders))
            countStatement = select (func.count ()).select_from (Permission).where (*conditions)

            total = session.exec (countStatement).one ()
            offset = (page.currentPage - 1) * page.limitPage
            permissions = session.exec (statement.offset (offset).limit (page.limitPage)).all ()

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
                data=[PermissionTransformerDto.fromPermission (item) for item in permissions],
            )
        finally:
            session.close ()

    async def allFiltered (
        self,
        orders: List[Any] = None,
        filters: List[Any] = None,
    ) -> List[Permission]:
        """
        Args:
            orders (List[Any])
            filters (List[Any])
        Returns:
            List[Permission]
        """
        session = self.getSession ()
        try:
            return list (
                session.exec (
                    select (Permission).where (*self._conditions (filters)).order_by (*self._orderBy (orders))
                ).all ()
            )
        finally:
            session.close ()

    async def findById (self, id: str) -> Optional[Permission]:
        """
        Args:
            id (str)
        Returns:
            Optional[Permission]
        """
        session = self.getSession ()
        try:
            return session.exec (select (Permission).where (Permission.id == id)).first ()
        finally:
            session.close ()

    async def findByNameGuard (self, name: str, guardName: str) -> Optional[Permission]:
        """
        Args:
            name (str)
            guardName (str)
        Returns:
            Optional[Permission]
        """
        session = self.getSession ()
        try:
            return session.exec (
                select (Permission).where (
                    Permission.name == name,
                    Permission.guard_name == guardName,
                )
            ).first ()
        finally:
            session.close ()

    async def findByNamesGuard (self, names: List[str], guardName: str) -> List[Permission]:
        """
        Args:
            names (List[str])
            guardName (str)
        Returns:
            List[Permission]
        """
        if not names:
            return []
        session = self.getSession ()
        try:
            return list (
                session.exec (
                    select (Permission).where (
                        Permission.name.in_ (names),
                        Permission.guard_name == guardName,
                    )
                ).all ()
            )
        finally:
            session.close ()

    async def create (self, name: str, guardName: str) -> Permission:
        """
        Args:
            name (str)
            guardName (str)
        Returns:
            Permission
        """
        session = self.getSession ()
        try:
            permission = Permission (
                id=str (ULID ()),
                name=name,
                guard_name=guardName,
            )
            session.add (permission)
            session.commit ()
            session.refresh (permission)
            return permission
        except Exception:
            session.rollback ()
            raise
        finally:
            session.close ()

    async def update (self, permission: Permission) -> Permission:
        """
        Args:
            permission (Permission)
        Returns:
            Permission
        """
        session = self.getSession ()
        try:
            attached = session.exec (
                select (Permission).where (Permission.id == permission.id)
            ).first ()
            if attached is None:
                return permission
            attached.name = permission.name
            attached.guard_name = permission.guard_name
            attached.updated_at = datetime.utcnow ()
            session.add (attached)
            session.commit ()
            session.refresh (attached)
            return attached
        except Exception:
            session.rollback ()
            raise
        finally:
            session.close ()

    async def delete (self, permission: Permission) -> None:
        """
        Args:
            permission (Permission)
        Returns:
            None
        """
        session = self.getSession ()
        try:
            attached = session.exec (
                select (Permission).where (Permission.id == permission.id)
            ).first ()
            if attached is None:
                return
            links = session.exec (
                select (RoleHasPermission).where (
                    RoleHasPermission.permission_id == attached.id
                )
            ).all ()
            for link in links:
                session.delete (link)
            session.delete (attached)
            session.commit ()
        except Exception:
            session.rollback ()
            raise
        finally:
            session.close ()

    async def findByIds (self, ids: List[str]) -> List[Permission]:
        """
        Args:
            ids (List[str])
        Returns:
            List[Permission]
        """
        if not ids:
            return []
        session = self.getSession ()
        try:
            return list (session.exec (select (Permission).where (Permission.id.in_ (ids))).all ())
        finally:
            session.close ()
