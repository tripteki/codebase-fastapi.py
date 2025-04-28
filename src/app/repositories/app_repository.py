from typing import Generic, TypeVar, Optional, List, Union, Protocol, Dict
from pydantic import BaseModel, Field

T = TypeVar ("T")

class SoftDeletion (BaseModel):
    """
    SoftDeletion (BaseModel)

    Attributes:
        deleted_at (Optional[str])
    """
    deleted_at: Optional[str] = None

class OffsetPaginationType (BaseModel):
    """
    OffsetPaginationType (BaseModel)

    Attributes:
        currentPage (Optional[int])
        limitPage (Optional[int])
    """
    currentPage: Optional[int] = Field (None, ge=1)
    limitPage: Optional[int] = Field (None, ge=1, le=100)

class CursorPaginationType (BaseModel):
    """
    CursorPaginationType (BaseModel)

    Attributes:
        cursorField (Optional[str])
        cursorPage (Optional[Union[int, str]])
        limitPage (Optional[int])
    """
    cursorField: Optional[str] = None
    cursorPage: Optional[Union[int, str]] = None
    limitPage: Optional[int] = Field (None, ge=1, le=100)

class OffsetPagination (BaseModel, Generic[T]):
    """
    OffsetPagination (BaseModel, Generic)

    Attributes:
        totalPage (int)
        perPage (int)
        currentPage (int)
        nextPage (Optional[int])
        previousPage (Optional[int])
        firstPage (int)
        lastPage (int)
        data (List[T])
    """
    totalPage: int
    perPage: int
    currentPage: int
    nextPage: Optional[int] = None
    previousPage: Optional[int] = None
    firstPage: int
    lastPage: int
    data: List[T]

class CursorPagination (BaseModel, Generic[T]):
    """
    CursorPagination (BaseModel, Generic)

    Attributes:
        nextCursorPage (Optional[Union[int, str]])
        data (List[T])
    """
    nextCursorPage: Optional[Union[int, str]] = None
    data: List[T]

class Orderization (BaseModel):
    """
    Orderization (BaseModel)

    Attributes:
        field (str)
        direction (str)
    """
    field: str
    direction: str = Field (..., pattern="^(asc|desc)$")

class Filterization (BaseModel):
    """
    Filterization (BaseModel)

    Attributes:
        field (str)
        search (str)
    """
    field: str
    search: str

class AppRepository (Protocol):
    """
    AppRepository (Protocol)
    """
    def soft_delete (self) -> SoftDeletion:
        """
        Returns:
            SoftDeletion
        """
        ...

    def order (self, orders: List[Orderization]) -> Dict[str, object]:
        """
        Args:
            orders (List[Orderization])
        Returns:
            Dict[str, object]
        """
        ...

    def filter (self, filters: List[Filterization]) -> Dict[str, object]:
        """
        Args:
            filters (List[Filterization])
        Returns:
            Dict[str, object]
        """
        ...

class AppPaginationOffsetRepository (Protocol):
    """
    AppPaginationOffsetRepository (Protocol)
    """
    async def offset_paginate_all (self, *args: object, **kwargs: object) -> OffsetPagination[object]:
        """
        Args:
            *args (object)
            **kwargs (object)
        Returns:
            OffsetPagination[object]
        """
        ...

class AppPaginationCursorRepository (Protocol):
    """
    AppPaginationCursorRepository (Protocol)
    """
    async def cursor_paginate_all (self, *args: object, **kwargs: object) -> CursorPagination[object]:
        """
        Args:
            *args (object)
            **kwargs (object)
        Returns:
            CursorPagination[object]
        """
        ...
