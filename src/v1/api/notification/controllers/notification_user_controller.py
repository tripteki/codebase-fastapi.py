from typing import Optional
from fastapi import APIRouter, Depends, Query, status, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from fastapi_limiter.depends import RateLimiter
from src.app.bases.app_security import security
from src.app.dependencies.app_auth_api_dependency import get_current_user
from src.app.dtos.app_dto import BatchPayloadType, Status, Description
from src.app.repositories.app_repository import OffsetPagination, OffsetPaginationType
from src.app.utils.app_query_parser import parseOrders, parseFilters
from src.app.utils.app_response_helper import getStandardResponses, getPaginationResponses
from src.v1.api.notification.dtos.notification_transformer_dto import NotificationTransformerDto, NotificationCountTransformerDto, NotificationUnreadTransformerDto
from src.v1.api.notification.dtos.notification_validator_dto import NotificationIdentifierDto
from src.v1.api.notification.services.notification_user_service import NotificationUserService
from src.v1.api.user.databases.models.user_model import User

notificationUserRouter = APIRouter (prefix="/api/v1/notifications", tags=["NotificationUser"])

@notificationUserRouter.get (
    "/",
    status_code=Status.OK,
    dependencies=[Depends (RateLimiter (times=10, seconds=60)), Depends (security)],
    response_model=OffsetPagination[NotificationTransformerDto],
    responses=getPaginationResponses (
        item_example={
            "id": "string",
            "user_id": "string",
            "type": "string",
            "data": {},
            "read_at": None,
            "created_at": "string",
            "updated_at": "string",
            "deleted_at": None
        },
        unauthorized=True,
        forbidden=True
    )
)
async def index (
    current_user: User = Depends (get_current_user),
    orders: Optional[str] = Query (None, description="Order by fields (e.g., 'created_at:desc,type:asc')"),
    filters: Optional[str] = Query (None, description="Filter by fields (e.g., 'type:info')"),
    limitPage: Optional[int] = Query (10, ge=1, le=100),
    currentPage: Optional[int] = Query (1, ge=1)
) -> OffsetPagination[NotificationTransformerDto]:
    """
    Index
    """
    page = OffsetPaginationType (currentPage=currentPage or 1, limitPage=limitPage or 10)
    return await NotificationUserService.all (current_user.id, parseOrders (orders), parseFilters (filters), page)

@notificationUserRouter.get (
    "/count",
    status_code=Status.OK,
    dependencies=[Depends (RateLimiter (times=10, seconds=60)), Depends (security)],
    response_model=NotificationCountTransformerDto,
    responses=getStandardResponses (unauthorized=True, forbidden=True)
)
async def count (
    current_user: User = Depends (get_current_user)
) -> NotificationCountTransformerDto:
    """
    Count
    """
    return await NotificationUserService.count (current_user.id)

@notificationUserRouter.put (
    "/read-all",
    status_code=Status.OK,
    dependencies=[Depends (RateLimiter (times=10, seconds=60)), Depends (security)],
    response_model=BatchPayloadType,
    responses=getStandardResponses (unauthorized=True, forbidden=True, bad_request=True)
)
async def readAll (
    current_user: User = Depends (get_current_user)
) -> BatchPayloadType:
    """
    Read All
    """
    return await NotificationUserService.readAll (current_user.id)

@notificationUserRouter.put (
    "/read/{id}",
    status_code=Status.OK,
    dependencies=[Depends (RateLimiter (times=10, seconds=60)), Depends (security)],
    response_model=NotificationTransformerDto,
    responses=getStandardResponses (unauthorized=True, forbidden=True, bad_request=True, not_found=True)
)
async def read (
    id: str,
    current_user: User = Depends (get_current_user)
) -> NotificationTransformerDto:
    """
    Read
    """
    return await NotificationUserService.read (current_user.id, id)

@notificationUserRouter.get (
    "/unread",
    status_code=Status.OK,
    dependencies=[Depends (RateLimiter (times=10, seconds=60)), Depends (security)],
    response_model=NotificationUnreadTransformerDto,
    responses=getStandardResponses (unauthorized=True, forbidden=True)
)
async def unread (
    current_user: User = Depends (get_current_user)
) -> NotificationUnreadTransformerDto:
    """
    Unread
    """
    return await NotificationUserService.unreadCount (current_user.id)

@notificationUserRouter.get (
    "/{id}",
    status_code=Status.OK,
    dependencies=[Depends (RateLimiter (times=10, seconds=60)), Depends (security)],
    response_model=NotificationTransformerDto,
    responses=getStandardResponses (unauthorized=True, forbidden=True, not_found=True)
)
async def show (
    id: str,
    current_user: User = Depends (get_current_user)
) -> NotificationTransformerDto:
    """
    Show
    """
    return await NotificationUserService.get (current_user.id, id)

@notificationUserRouter.delete (
    "/{id}",
    status_code=Status.OK,
    dependencies=[Depends (RateLimiter (times=10, seconds=60)), Depends (security)],
    response_model=NotificationTransformerDto,
    responses=getStandardResponses (unauthorized=True, forbidden=True, not_found=True)
)
async def delete (
    id: str,
    current_user: User = Depends (get_current_user)
) -> NotificationTransformerDto:
    """
    Delete
    """
    return await NotificationUserService.delete (current_user.id, id)
