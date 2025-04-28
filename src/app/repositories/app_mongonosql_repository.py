from typing import TypeVar, Generic, Optional, List, Dict, Callable
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorClient
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

class AppMongonosqlRepository (Generic[T]):
    """
    AppMongonosqlRepository (Generic)
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

    def order (self, orders: List[Orderization]) -> List[tuple[str, int]]:
        """
        Args:
            orders (List[Orderization])
        Returns:
            List[tuple[str, int]]
        """
        order_by = []
        for order in orders:
            direction = 1 if order.direction == "asc" else -1
            order_by.append ((order.field, direction))
        return order_by

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
            conditions[field] = {"$regex": search, "$options": "i"}
        return conditions

    async def offset_paginate_all (
        self,
        collection_name: str,
        query: Dict[str, object],
        page: OffsetPaginationType,
        database: AsyncIOMotorDatabase
    ) -> OffsetPagination[T]:
        """
        Args:
            collection_name (str)
            query (Dict[str, object])
            page (OffsetPaginationType)
            database (AsyncIOMotorDatabase)
        Returns:
            OffsetPagination[T]
        """
        try:
            collection = database[collection_name]

            filter_query = query.get ("filter", {})
            sort_query = query.get ("sort", [])

            total = await collection.count_documents (filter_query)

            skip = (page.currentPage - 1) * page.limitPage
            limit = page.limitPage

            cursor = collection.find (filter_query)

            if sort_query:
                cursor = cursor.sort (sort_query)

            cursor = cursor.skip (skip).limit (limit)

            results = await cursor.to_list (length=limit)

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
                data=results
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
        collection_name: str,
        query: Dict[str, object],
        page: CursorPaginationType,
        database: AsyncIOMotorDatabase
    ) -> CursorPagination[T]:
        """
        Args:
            collection_name (str)
            query (Dict[str, object])
            page (CursorPaginationType)
            database (AsyncIOMotorDatabase)
        Returns:
            CursorPagination[T]
        """
        try:
            collection = database[collection_name]

            filter_query = query.get ("filter", {})
            sort_query = query.get ("sort", [(page.cursorField, 1)])

            if page.cursorPage:
                filter_query[page.cursorField] = {"$gt": page.cursorPage}

            cursor = collection.find (filter_query)

            if sort_query:
                cursor = cursor.sort (sort_query)

            cursor = cursor.limit (page.limitPage + 1)

            results = await cursor.to_list (length=page.limitPage + 1)

            has_next_page = len (results) > page.limitPage

            if has_next_page:
                data = results[:-1]
                next_cursor = data[-1].get (page.cursorField) if data else None
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
            content = await callback ()
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
            content = await callback ()
            return content

        except Exception as e:
            self.logger.warning (f"Access get error: {e}")
            raise e

    async def mutate (
        self,
        callback: Callable[[AsyncIOMotorDatabase], Optional[T]],
        database: AsyncIOMotorDatabase
    ) -> Optional[T]:
        """
        Args:
            callback (Callable)
            database (AsyncIOMotorDatabase)
        Returns:
            Optional[T]
        """
        try:
            content = await callback (database)
            return content

        except Exception as e:
            self.logger.warning (f"Mutation error: {e}")
            raise e
