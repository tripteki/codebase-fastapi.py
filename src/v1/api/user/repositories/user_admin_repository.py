from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlmodel import Session, select
from ulid import ULID
from src.app.bases.app_auth import AppAuth
from src.app.bases.app_database import AppDatabase
from src.app.repositories.app_postgresql_repository import AppPostgresqlRepository
from src.app.repositories.app_repository import OffsetPagination, OffsetPaginationType, CursorPagination, CursorPaginationType, Orderization, Filterization
from src.v1.api.user.databases.models.user_model import User
from src.v1.api.user.dtos.user_transformer_dto import UserTransformerDto

class UserAdminRepository (AppPostgresqlRepository[User]):
    """
    UserAdminRepository
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
    ) -> OffsetPagination[UserTransformerDto]:
        """
        Args:
            userId (str)
            orders (List[Orderization])
            filters (List[Filterization])
            page (OffsetPaginationType)
        Returns:
            OffsetPagination[UserTransformerDto]
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

            result = await self.offset_paginate_all (
                model=User,
                query=query,
                page=page,
                session=session
            )

            data = [UserTransformerDto (
                id=user.id,
                name=user.name,
                email=user.email,
                email_verified_at=user.email_verified_at,
                created_at=user.created_at,
                updated_at=user.updated_at,
                deleted_at=user.deleted_at
            ) for user in result.data]

            return OffsetPagination (
                totalPage=result.totalPage,
                perPage=result.perPage,
                currentPage=result.currentPage,
                nextPage=result.nextPage,
                previousPage=result.previousPage,
                firstPage=result.firstPage,
                lastPage=result.lastPage,
                data=data
            )
        finally:
            session.close ()

    async def allCursor (
        self,
        userId: str,
        orders: List[Orderization] = None,
        filters: List[Filterization] = None,
        page: CursorPaginationType = None
    ) -> CursorPagination[User]:
        """
        Args:
            userId (str)
            orders (List[Orderization])
            filters (List[Filterization])
            page (CursorPaginationType)
        Returns:
            CursorPagination[User]
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
                model=User,
                query=query,
                page=page,
                session=session
            )
        finally:
            session.close ()

    @staticmethod
    async def get (userId: str, id: str) -> Optional[User]:
        """
        Args:
            userId (str)
            id (str)
        Returns:
            Optional[User]
        """
        session = UserAdminRepository.getSession ()
        try:
            statement = select (User).where (User.id == id, User.deleted_at == None)
            result = session.exec (statement).first ()
            return result
        finally:
            session.close ()

    @staticmethod
    async def update (userId: str, id: str, data: Dict[str, Any]) -> Optional[User]:
        """
        Args:
            userId (str)
            id (str)
            data (Dict[str, Any])
        Returns:
            Optional[User]
        """
        session = UserAdminRepository.getSession ()
        try:
            statement = select (User).where (User.id == id, User.deleted_at == None)
            user = session.exec (statement).first ()
            if not user:
                return None
            if "name" in data and data["name"] is not None:
                user.name = data["name"]
            if "email" in data and data["email"] is not None:
                user.email = data["email"]
            if "password" in data and data["password"] is not None:
                user.password = AppAuth.hashPassword (data["password"])
            user.updated_at = datetime.utcnow ()
            session.add (user)
            session.commit ()
            session.refresh (user)
            return user
        finally:
            session.close ()

    @staticmethod
    async def create (userId: str, data: Dict[str, Any]) -> Optional[User]:
        """
        Args:
            userId (str)
            data (Dict[str, Any])
        Returns:
            Optional[User]
        """
        session = UserAdminRepository.getSession ()
        try:
            user = User (
                id=str (ULID ()),
                name=data.get ("name"),
                email=data.get ("email"),
                password=AppAuth.hashPassword (data.get ("password")),
                email_verified_at=datetime.utcnow (),
                created_at=datetime.utcnow (),
                updated_at=datetime.utcnow ()
            )
            session.add (user)
            session.commit ()
            session.refresh (user)
            return user
        finally:
            session.close ()

    @staticmethod
    async def restore (userId: str, id: str) -> Optional[User]:
        """
        Args:
            userId (str)
            id (str)
        Returns:
            Optional[User]
        """
        session = UserAdminRepository.getSession ()
        try:
            statement = select (User).where (User.id == id)
            user = session.exec (statement).first ()
            if not user:
                return None
            user.deleted_at = None
            user.updated_at = datetime.utcnow ()
            session.add (user)
            session.commit ()
            session.refresh (user)
            return user
        finally:
            session.close ()

    @staticmethod
    async def delete (userId: str, id: str) -> Optional[User]:
        """
        Args:
            userId (str)
            id (str)
        Returns:
            Optional[User]
        """
        session = UserAdminRepository.getSession ()
        try:
            statement = select (User).where (User.id == id, User.deleted_at == None)
            user = session.exec (statement).first ()
            if not user:
                return None
            user.deleted_at = datetime.utcnow ()
            user.updated_at = datetime.utcnow ()
            session.add (user)
            session.commit ()
            session.refresh (user)
            return user
        finally:
            session.close ()

    @staticmethod
    async def verify (userId: str, id: str) -> Optional[User]:
        """
        Args:
            userId (str)
            id (str)
        Returns:
            Optional[User]
        """
        session = UserAdminRepository.getSession ()
        try:
            statement = select (User).where (User.id == id, User.deleted_at == None, User.email_verified_at == None)
            user = session.exec (statement).first ()
            if not user:
                return None
            user.email_verified_at = datetime.utcnow ()
            session.add (user)
            session.commit ()
            session.refresh (user)
            return user
        finally:
            session.close ()
