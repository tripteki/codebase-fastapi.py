from typing import Generic, TypeVar, Optional, List, Union, Protocol, Dict, Any
from pydantic import BaseModel, Field

T = TypeVar ("T")

class SoftDeletion (BaseModel):
    """
    SoftDeletion
    """
    deleted_at: Optional[str] = None

class OffsetPaginationType (BaseModel):
    """
    OffsetPaginationType
    """
    currentPage: Optional[int] = Field (None, ge=1)
    limitPage: Optional[int] = Field (None, ge=1, le=100)

class CursorPaginationType (BaseModel):
    """
    CursorPaginationType
    """
    cursorField: Optional[str] = None
    cursorPage: Optional[Union[int, str]] = None
    limitPage: Optional[int] = Field (None, ge=1, le=100)

class OffsetPagination (BaseModel, Generic[T]):
    """
    OffsetPagination
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
    CursorPagination
    """
    nextCursorPage: Optional[Union[int, str]] = None
    data: List[T]

class Orderization (BaseModel):
    """
    Orderization
    """
    field: str
    direction: str = Field (..., pattern="^(asc|desc)$")

class Filterization (BaseModel):
    """
    Filterization
    """
    field: str
    search: str

class AppRepository (Protocol):
    """
    AppRepository
    """
    def soft_delete (self) -> SoftDeletion:
        """
        Args:
        Returns:
            SoftDeletion
        """
        ...

    def order (self, orders: List[Orderization]) -> Any:
        """
        Args:
            orders (List[Orderization])
        Returns:
            Any
        """
        ...

    def filter (self, filters: List[Filterization]) -> Any:
        """
        Args:
            filters (List[Filterization])
        Returns:
            Any
        """
        ...

class AppPaginationOffsetRepository (Protocol):
    """
    AppPaginationOffsetRepository
    """
    async def offset_paginate_all (self, *args, **kwargs) -> OffsetPagination:
        """
        Args:
            args
            kwargs
        Returns:
            OffsetPagination
        """
        ...

class AppPaginationCursorRepository (Protocol):
    """
    AppPaginationCursorRepository
    """
    async def cursor_paginate_all (self, *args, **kwargs) -> CursorPagination:
        """
        Args:
            args
            kwargs
        Returns:
            CursorPagination
        """
        ...
