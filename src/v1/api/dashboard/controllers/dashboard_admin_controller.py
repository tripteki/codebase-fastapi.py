from typing import Optional
from fastapi import APIRouter, Depends, Query
from src.app.bases.app_security import security
from src.app.dependencies.app_auth_api_dependency import get_current_user
from src.app.dependencies.app_rate_limit import rateLimit
from src.app.dtos.app_dto import Status
from src.app.utils.app_response_helper import getStandardResponses
from src.v1.api.dashboard.dtos.dashboard_transformer_dto import DashboardTransformerDto
from src.v1.api.dashboard.services.dashboard_admin_service import DashboardAdminService
from src.v1.api.user.databases.models.user_model import User

dashboardAdminRouter = APIRouter (prefix="/api/v1/admin/dashboard", tags=["DashboardAdmin"])

@dashboardAdminRouter.get (
    "/",
    status_code=Status.OK,
    dependencies=[rateLimit (times=30, seconds=60), Depends (security)],
    response_model=DashboardTransformerDto,
    responses=getStandardResponses (unauthorized=True, forbidden=True),
)
async def show (
    current_user: User = Depends (get_current_user),
    period: Optional[str] = Query ("30d", description="today|7d|30d|custom"),
    date_from: Optional[str] = Query (None),
    date_to: Optional[str] = Query (None),
) -> DashboardTransformerDto:
    """
    Show
    """
    return await DashboardAdminService.get (
        current_user.id,
        period=period or "30d",
        dateFrom=date_from,
        dateTo=date_to,
    )
