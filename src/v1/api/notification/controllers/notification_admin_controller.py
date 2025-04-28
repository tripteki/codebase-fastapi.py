from typing import Optional
from fastapi import APIRouter, Depends, Query, status, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from fastapi_limiter.depends import RateLimiter
from src.app.bases.app_security import security
from src.app.dependencies.app_auth_api_dependency import get_current_user
from src.app.dtos.app_dto import Status, Description
from src.app.repositories.app_repository import OffsetPagination, OffsetPaginationType
from src.app.utils.app_query_parser import parseOrders, parseFilters
from src.app.utils.app_response_helper import getStandardResponses, getPaginationResponses
from src.v1.api.notification.dtos.notification_transformer_dto import NotificationTransformerDto
from src.v1.api.notification.dtos.notification_validator_dto import NotificationIdentifierDto, NotificationCreateValidatorDto, NotificationUpdateValidatorDto
from src.v1.api.notification.services.notification_admin_service import NotificationAdminService
from src.v1.api.user.databases.models.user_model import User

notificationAdminRouter = APIRouter (prefix="/api/v1/admin/notifications", tags=["NotificationAdmin"])

@notificationAdminRouter.get (
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
    filters: Optional[str] = Query (None, description="Filter by fields (e.g., 'type:info,user_id:123')"),
    limitPage: Optional[int] = Query (10, ge=1, le=100),
    currentPage: Optional[int] = Query (1, ge=1)
) -> OffsetPagination[NotificationTransformerDto]:
    """
    Index
    """
    page = OffsetPaginationType (currentPage=currentPage or 1, limitPage=limitPage or 10)
    return await NotificationAdminService.all (current_user.id, parseOrders (orders), parseFilters (filters), page)

@notificationAdminRouter.get (
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
    return await NotificationAdminService.get (current_user.id, id)

@notificationAdminRouter.delete (
    "/activate/{id}",
    status_code=Status.OK,
    dependencies=[Depends (RateLimiter (times=10, seconds=60)), Depends (security)],
    response_model=NotificationTransformerDto,
    responses=getStandardResponses (unauthorized=True, forbidden=True, not_found=True)
)
async def activate (
    id: str,
    current_user: User = Depends (get_current_user)
) -> NotificationTransformerDto:
    """
    Activate
    """
    return await NotificationAdminService.restore (current_user.id, id)

@notificationAdminRouter.delete (
    "/deactivate/{id}",
    status_code=Status.OK,
    dependencies=[Depends (RateLimiter (times=10, seconds=60)), Depends (security)],
    response_model=NotificationTransformerDto,
    responses=getStandardResponses (unauthorized=True, forbidden=True, not_found=True)
)
async def deactivate (
    id: str,
    current_user: User = Depends (get_current_user)
) -> NotificationTransformerDto:
    """
    Deactivate
    """
    return await NotificationAdminService.delete (current_user.id, id)
