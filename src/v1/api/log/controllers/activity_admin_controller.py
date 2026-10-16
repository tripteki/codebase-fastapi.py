from typing import Optional
from fastapi import APIRouter, Depends, Query
from src.app.bases.app_security import security
from src.app.dependencies.app_permission_dependency import requirePermission
from src.app.dependencies.app_rate_limit import rateLimit
from src.app.dtos.app_dto import Status
from src.app.repositories.app_repository import OffsetPagination
from src.app.utils.app_query_parser import parseFilters, parseOrders
from src.app.utils.app_response_helper import getPaginationResponses, getStandardResponses
from src.v1.api.log.dtos.activity_transformer_dto import ActivityTransformerDto
from src.v1.api.log.services.activity_admin_service import ActivityAdminService
from src.v1.api.user.databases.models.user_model import User

activityAdminRouter = APIRouter (prefix="/api/v1/admin/activities", tags=["ActivityAdmin"])

@activityAdminRouter.get (
    "/",
    status_code=Status.OK,
    dependencies=[rateLimit (times=10, seconds=60), Depends (security)],
    response_model=OffsetPagination[ActivityTransformerDto],
    responses=getPaginationResponses (unauthorized=True, forbidden=True),
)
async def index (
    current_user: User = Depends (requirePermission ("activity.view")),
    orders: Optional[str] = Query (None, description="Order by fields (e.g., 'created_at:desc')"),
    filters: Optional[str] = Query (
        None,
        description="Filter by fields (e.g., 'q:user,subject_type:User,date_from:2026-01-01,date_to:2026-12-31,causer:admin')",
    ),
    limitPage: Optional[int] = Query (10, ge=1, le=100),
    currentPage: Optional[int] = Query (1, ge=1),
) -> OffsetPagination[ActivityTransformerDto]:
    """
    Index
    """
    page = {"currentPage": currentPage or 1, "limitPage": limitPage or 10}
    return await ActivityAdminService.all (current_user.id, parseOrders (orders), parseFilters (filters), page)

@activityAdminRouter.get (
    "/{id}",
    status_code=Status.OK,
    dependencies=[rateLimit (times=10, seconds=60), Depends (security)],
    response_model=ActivityTransformerDto,
    responses=getStandardResponses (unauthorized=True, forbidden=True, not_found=True),
)
async def show (
    id: str,
    current_user: User = Depends (requirePermission ("activity.view")),
) -> ActivityTransformerDto:
    """
    Show
    """
    return await ActivityAdminService.get (current_user.id, id)
