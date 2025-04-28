from datetime import datetime
from typing import Optional, List, Dict
from sqlmodel import Session, select, func
from ulid import ULID
from src.app.bases.app_database import AppDatabase
from src.app.repositories.app_postgresql_repository import AppPostgresqlRepository
from src.app.repositories.app_repository import OffsetPagination, OffsetPaginationType, CursorPagination, CursorPaginationType, Orderization, Filterization
from src.v1.api.notification.databases.models.notification_model import Notification

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
                "where": {
                    **self.soft_delete (),
                    "user_id": userId
                },
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
            session.add (notification)
            session.commit ()
            session.refresh (notification)
            return notification
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
            for notification in notifications:
                notification.read_at = datetime.utcnow ()
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
