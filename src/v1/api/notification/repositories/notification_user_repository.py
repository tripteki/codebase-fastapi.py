from datetime import datetime
from typing import Any, Optional, List, Dict
from sqlmodel import Session, col, select
from sqlalchemy import func
from ulid import ULID
from src.app.bases.app_database import AppDatabase
from src.app.repositories.app_postgresql_repository import AppPostgresqlRepository
from src.app.repositories.app_repository import OffsetPagination, OffsetPaginationType, CursorPagination, CursorPaginationType, Orderization, Filterization
from src.v1.api.notification.databases.models.notification_model import Notification

SORTABLE_FIELDS = ("type", "read_at", "created_at", "updated_at")

class NotificationUserRepository (AppPostgresqlRepository[Notification]):
    """
    NotificationUserRepository (AppPostgresqlRepository)
    """
    def __init__ (self) -> None:
        """
        Returns:
        """
        super ().__init__ ()

    @staticmethod
    def getSession () -> Session:
        """
        Returns:
            Session
        """
        engine = AppDatabase.databasePostgresql ()
        return Session (engine)

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
        return normalized or [("updated_at", "desc")]

    async def allOffset (
        self,
        userId: str,
        orders: List[Orderization] = None,
        filters: List[Filterization] = None,
        page: OffsetPaginationType = None
    ) -> OffsetPagination[Notification]:
        """
        Args:
            userId (str)
            orders (List[Orderization])
            filters (List[Filterization])
            page (OffsetPaginationType)
        Returns:
            OffsetPagination[Notification]
        """
        page = page or OffsetPaginationType (currentPage=1, limitPage=10)
        filterMap = self._normalizeFilters (filters)
        orderPairs = self._normalizeOrders (orders)

        session = self.getSession ()
        try:
            statement = select (Notification).where (
                Notification.user_id == userId,
                Notification.deleted_at == None,
            )
            countStatement = select (func.count ()).select_from (Notification).where (
                Notification.user_id == userId,
                Notification.deleted_at == None,
            )
            statusValue = (filterMap.get ("status") or "").lower ()
            if statusValue == "unread":
                statement = statement.where (Notification.read_at == None)
                countStatement = countStatement.where (Notification.read_at == None)
            elif statusValue == "read":
                statement = statement.where (Notification.read_at != None)
                countStatement = countStatement.where (Notification.read_at != None)
            notificationType = filterMap.get ("type")
            if notificationType:
                statement = statement.where (Notification.type == notificationType)
                countStatement = countStatement.where (Notification.type == notificationType)
            q = filterMap.get ("q") or filterMap.get ("search")
            if q:
                pattern = f"%{q}%"
                statement = statement.where (col (Notification.type).ilike (pattern))
                countStatement = countStatement.where (col (Notification.type).ilike (pattern))
            for field, direction in orderPairs:
                if field not in SORTABLE_FIELDS:
                    continue
                column = getattr (Notification, field)
                statement = statement.order_by (column.desc () if direction == "desc" else column.asc ())
            total = int (session.exec (countStatement).one ())
            offset = (page.currentPage - 1) * page.limitPage
            rows = session.exec (statement.offset (offset).limit (page.limitPage)).all ()
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
                data=list (rows),
            )
        finally:
            session.close ()

    async def allCursor (
        self,
        userId: str,
        orders: List[Orderization] = None,
        filters: List[Filterization] = None,
        page: CursorPaginationType = None
    ) -> CursorPagination[Notification]:
        """
        Args:
            userId (str)
            orders (List[Orderization])
            filters (List[Filterization])
            page (CursorPaginationType)
        Returns:
            CursorPagination[Notification]
        """
        orders = orders or []
        filters = filters or []
        page = page or CursorPaginationType (cursorField="id", cursorPage=None, limitPage=10)

        page.cursorField = "id"

        session = self.getSession ()
        try:
            query = {
                "where": {
                    **self.soft_delete (),
                    "user_id": userId
                },
            }

            if filters:
                query["where"].update (self.filter (filters))

            if orders:
                query.update (self.order (orders))

            return await self.cursor_paginate_all (
                model=Notification,
                query=query,
                page=page,
                session=session
            )
        finally:
            session.close ()

    @staticmethod
    async def get (userId: str, id: str) -> Optional[Notification]:
        """
        Args:
            userId (str)
            id (str)
        Returns:
            Optional[Notification]
        """
        session = NotificationUserRepository.getSession ()
        try:
            statement = select (Notification).where (Notification.id == id, Notification.user_id == userId, Notification.deleted_at == None)
            result = session.exec (statement).first ()
            return result
        finally:
            session.close ()

    @staticmethod
    async def create (userId: str, data: Dict[str, object]) -> Notification:
        """
        Args:
            userId (str)
            data (Dict[str, object])
        Returns:
            Notification
        """
        session = NotificationUserRepository.getSession ()
        try:
            notification = Notification (
                user_id=userId,
                type=str (data.get ("type", "")),
                data=data.get ("data", {}),
                created_at=datetime.utcnow (),
                updated_at=datetime.utcnow ()
            )
            session.add (notification)
            session.commit ()
            session.refresh (notification)
            return notification
        finally:
            session.close ()

    @staticmethod
    async def read (userId: str, id: str) -> Optional[Notification]:
        """
        Args:
            userId (str)
            id (str)
        Returns:
            Optional[Notification]
        """
        session = NotificationUserRepository.getSession ()
        try:
            statement = select (Notification).where (Notification.id == id, Notification.user_id == userId, Notification.deleted_at == None)
            notification = session.exec (statement).first ()
            if not notification:
                return None
            notification.read_at = datetime.utcnow ()
            notification.updated_at = datetime.utcnow ()
            session.add (notification)
            session.commit ()
            session.refresh (notification)
            return notification
        finally:
            session.close ()

    @staticmethod
    async def unread (userId: str, id: str) -> Optional[Notification]:
        """
        Args:
            userId (str)
            id (str)
        Returns:
            Optional[Notification]
        """
        session = NotificationUserRepository.getSession ()
        try:
            statement = select (Notification).where (Notification.id == id, Notification.user_id == userId, Notification.deleted_at == None)
            notification = session.exec (statement).first ()
            if not notification:
                return None
            notification.read_at = None
            notification.updated_at = datetime.utcnow ()
            session.add (notification)
            session.commit ()
            session.refresh (notification)
            return notification
        finally:
            session.close ()

    @staticmethod
    async def unreadCount (userId: str) -> int:
        """
        Args:
            userId (str)
        Returns:
            int
        """
        session = NotificationUserRepository.getSession ()
        try:
            return session.exec (
                select (func.count ()).select_from (Notification).where (
                    Notification.user_id == userId,
                    Notification.deleted_at == None,
                    Notification.read_at == None,
                )
            ).one ()
        finally:
            session.close ()

    @staticmethod
    async def unreadAll (userId: str) -> int:
        """
        Args:
            userId (str)
        Returns:
            int
        """
        session = NotificationUserRepository.getSession ()
        try:
            notifications = session.exec (
                select (Notification).where (
                    Notification.user_id == userId,
                    Notification.deleted_at == None,
                    Notification.read_at != None,
                )
            ).all ()
            now = datetime.utcnow ()
            for notification in notifications:
                notification.read_at = None
                notification.updated_at = now
                session.add (notification)
            session.commit ()
            return len (notifications)
        finally:
            session.close ()

    @staticmethod
    async def readAll (userId: str) -> int:
        """
        Args:
            userId (str)
        Returns:
            int
        """
        session = NotificationUserRepository.getSession ()
        try:
            statement = select (Notification).where (Notification.user_id == userId, Notification.deleted_at == None, Notification.read_at == None)
            notifications = session.exec (statement).all ()
            count = 0
            now = datetime.utcnow ()
            for notification in notifications:
                notification.read_at = now
                notification.updated_at = now
                session.add (notification)
                count += 1
            session.commit ()
            return count
        finally:
            session.close ()

    @staticmethod
    async def delete (userId: str, id: str) -> Optional[Notification]:
        """
        Args:
            userId (str)
            id (str)
        Returns:
            Optional[Notification]
        """
        session = NotificationUserRepository.getSession ()
        try:
            statement = select (Notification).where (Notification.id == id, Notification.user_id == userId, Notification.deleted_at == None)
            notification = session.exec (statement).first ()
            if not notification:
                return None
            notification.deleted_at = datetime.utcnow ()
            notification.updated_at = datetime.utcnow ()
            session.add (notification)
            session.commit ()
            session.refresh (notification)
            return notification
        finally:
            session.close ()

    @staticmethod
    async def deleteAll (userId: str) -> int:
        """
        Args:
            userId (str)
        Returns:
            int
        """
        session = NotificationUserRepository.getSession ()
        try:
            notifications = session.exec (
                select (Notification).where (Notification.user_id == userId, Notification.deleted_at == None)
            ).all ()
            now = datetime.utcnow ()
            for notification in notifications:
                notification.deleted_at = now
                notification.updated_at = now
                session.add (notification)
            session.commit ()
            return len (notifications)
        finally:
            session.close ()

    @staticmethod
    async def count (userId: str) -> int:
        """
        Args:
            userId (str)
        Returns:
            int
        """
        session = NotificationUserRepository.getSession ()
        try:
            statement = select (func.count ()).select_from (Notification).where (Notification.user_id == userId, Notification.deleted_at == None)
            count = session.exec (statement).one ()
            return count
        finally:
            session.close ()
