from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlmodel import Session, select, func
from ulid import ULID
from src.app.bases.app_database import AppDatabase
from src.app.repositories.app_postgresql_repository import AppPostgresqlRepository
from src.app.repositories.app_repository import OffsetPagination, OffsetPaginationType, CursorPagination, CursorPaginationType, Orderization, Filterization
from src.v1.api.notification.databases.models.notification_model import Notification

class NotificationAdminRepository (AppPostgresqlRepository[Notification]):
    """
    NotificationAdminRepository
    """

    def __init__ (self):
        """
        Args:
        Returns:
        """
        super ().__init__ ()

    @staticmethod
    def getSession () -> Session:
        """
        Args:
        Returns:
            Session
        """
        engine = AppDatabase.databasePostgresql ()
        return Session (engine)

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
        orders = orders or []
        filters = filters or []
        page = page or OffsetPaginationType (currentPage=1, limitPage=10)

        session = self.getSession ()
        try:
            query = {
                "where": self.soft_delete (),
            }

            if filters:
                query["where"].update (self.filter (filters))

            if orders:
                query.update (self.order (orders))

            return await self.offset_paginate_all (
                model=Notification,
                query=query,
                page=page,
                session=session
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
                "where": self.soft_delete (),
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
        session = NotificationAdminRepository.getSession ()
        try:
            statement = select (Notification).where (Notification.id == id, Notification.deleted_at == None)
            result = session.exec (statement).first ()
            return result
        finally:
            session.close ()

    @staticmethod
    async def restore (userId: str, id: str) -> Optional[Notification]:
        """
        Args:
            userId (str)
            id (str)
        Returns:
            Optional[Notification]
        """
        session = NotificationAdminRepository.getSession ()
        try:
            statement = select (Notification).where (Notification.id == id)
            notification = session.exec (statement).first ()
            if not notification:
                return None
            notification.deleted_at = None
            notification.updated_at = datetime.utcnow ()
            session.add (notification)
            session.commit ()
            session.refresh (notification)
            return notification
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
        session = NotificationAdminRepository.getSession ()
        try:
            statement = select (Notification).where (Notification.id == id, Notification.deleted_at == None)
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
