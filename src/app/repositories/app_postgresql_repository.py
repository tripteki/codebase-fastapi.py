from typing import TypeVar, Generic, Optional, List, Dict, Callable
from sqlmodel import Session, select, func
from sqlalchemy import text
from src.app.bases.app_database import AppDatabase
from src.app.repositories.app_repository import (
    OffsetPaginationType,
    CursorPaginationType,
    OffsetPagination,
    CursorPagination,
    SoftDeletion,
    Orderization,
    Filterization,
)
import logging

T = TypeVar ("T")

class AppPostgresqlRepository (Generic[T]):
    """
    AppPostgresqlRepository (Generic)
    """
    def __init__ (self) -> None:
        """
        Returns:
        """
        self.logger = logging.getLogger (self.__class__.__name__)

    def soft_delete (self) -> SoftDeletion:
        """
        Returns:
            SoftDeletion
        """
        return {"deleted_at": None}

    def order (self, orders: List[Orderization]) -> Dict[str, object]:
        """
        Args:
            orders (List[Orderization])
        Returns:
            Dict[str, object]
        """
        order_by = []
        for order in orders:
            direction = text (f"{order.field} {order.direction}")
            order_by.append (direction)
        return {"order_by": order_by}

    def filter (self, filters: List[Filterization]) -> Dict[str, object]:
        """
        Args:
            filters (List[Filterization])
        Returns:
            Dict[str, object]
        """
        conditions = {}
        for f in filters:
            field = f.field
            search = f.search
            conditions[field] = {"contains": search}
        return conditions

    async def offset_paginate_all (
        self,
        model: type[T],
        query: Dict[str, object],
        page: OffsetPaginationType,
        session: Session
    ) -> OffsetPagination[T]:
        """
        Args:
            model (type[T])
            query (Dict[str, object])
            page (OffsetPaginationType)
            session (Session)
        Returns:
            OffsetPagination[T]
        """
        try:
            statement = select (model)

            if "where" in query:
                for key, value in query["where"].items ():
                    statement = statement.where (getattr (model, key) == value)

            if "order_by" in query:
                for order in query["order_by"]:
                    statement = statement.order_by (order)

            count_statement = select (func.count ()).select_from (model)
            if "where" in query:
                for key, value in query["where"].items ():
                    count_statement = count_statement.where (getattr (model, key) == value)

            total = session.exec (count_statement).one ()

            offset = (page.currentPage - 1) * page.limitPage
            statement = statement.offset (offset).limit (page.limitPage)

            results = session.exec (statement).all ()

            per_page = page.limitPage
            current_page = page.currentPage
            last_page = (total + per_page - 1) // per_page if total > 0 else 1

            return OffsetPagination (
                totalPage=last_page,
                perPage=per_page,
                currentPage=current_page,
                nextPage=current_page + 1 if current_page < last_page else None,
                previousPage=current_page - 1 if current_page > 1 else None,
                firstPage=1,
                lastPage=last_page,
                data=list (results)
            )

        except Exception as e:
            self.logger.warning (f"Pagination error: {e}")

            return OffsetPagination (
                totalPage=1,
                perPage=page.limitPage,
                currentPage=page.currentPage,
                nextPage=None,
                previousPage=None,
                firstPage=1,
                lastPage=1,
                data=[]
            )

    async def cursor_paginate_all (
        self,
        model: type[T],
        query: Dict[str, object],
        page: CursorPaginationType,
        session: Session
    ) -> CursorPagination[T]:
        """
        Args:
            model (type[T])
            query (Dict[str, object])
            page (CursorPaginationType)
            session (Session)
        Returns:
            CursorPagination[T]
        """
        try:
            statement = select (model)

            if "where" in query:
                for key, value in query["where"].items ():
                    statement = statement.where (getattr (model, key) == value)

            if page.cursorPage:
                cursor_field = getattr (model, page.cursorField)
                statement = statement.where (cursor_field > page.cursorPage)

            if "order_by" in query:
                for order in query["order_by"]:
                    statement = statement.order_by (order)
            else:
                statement = statement.order_by (getattr (model, page.cursorField))

            statement = statement.limit (page.limitPage + 1)

            results = list (session.exec (statement).all ())

            has_next_page = len (results) > page.limitPage

            if has_next_page:
                data = results[:-1]
                next_cursor = getattr (results[-2], page.cursorField) if len (results) > 1 else None
            else:
                data = results
                next_cursor = None

            return CursorPagination (
                nextCursorPage=next_cursor,
                data=data
            )

        except Exception as e:
            self.logger.warning (f"Cursor pagination error: {e}")

            return CursorPagination (
                nextCursorPage=None,
                data=[]
            )

    async def access_all (
        self,
        callback: Callable[[], List[T]],
    ) -> List[T]:
        """
        Args:
            callback (Callable)
        Returns:
            List[T]
        """
        try:
            content = callback ()
            return content

        except Exception as e:
            self.logger.warning (f"Access all error: {e}")
            raise e

    async def access_get (
        self,
        callback: Callable[[], Optional[T]],
    ) -> Optional[T]:
        """
        Args:
            callback (Callable)
        Returns:
            Optional[T]
        """
        try:
            content = callback ()
            return content

        except Exception as e:
            self.logger.warning (f"Access get error: {e}")
            raise e

    async def mutate (
        self,
        callback: Callable[[Session], Optional[T]],
        session: Session
    ) -> Optional[T]:
        """
        Args:
            callback (Callable)
            session (Session)
        Returns:
            Optional[T]
        """
        try:
            content = callback (session)
            session.commit ()
            return content

        except Exception as e:
            session.rollback ()
            self.logger.warning (f"Mutation error: {e}")
            raise e
