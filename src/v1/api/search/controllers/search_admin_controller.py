from typing import Optional
from fastapi import APIRouter, Depends, Query
from src.app.bases.app_security import security
from src.app.dependencies.app_auth_api_dependency import get_current_user
from src.app.dependencies.app_rate_limit import rateLimit
from src.app.dtos.app_dto import Status
from src.app.utils.app_response_helper import getStandardResponses
from src.v1.api.search.dtos.search_transformer_dto import SearchTransformerDto
from src.v1.api.search.services.search_admin_service import SearchAdminService
from src.v1.api.user.databases.models.user_model import User

searchAdminRouter = APIRouter (prefix="/api/v1/admin/search", tags=["SearchAdmin"])

@searchAdminRouter.get (
    "/",
    status_code=Status.OK,
    dependencies=[rateLimit (times=60, seconds=60), Depends (security)],
    response_model=SearchTransformerDto,
    responses=getStandardResponses (unauthorized=True),
)
async def index (
    current_user: User = Depends (get_current_user),
    q: Optional[str] = Query (None, description="Search query (min 2 chars)"),
    category: Optional[str] = Query ("all", description="all|users|roles|permissions|activities"),
) -> SearchTransformerDto:
    """
    Index
    """
    return await SearchAdminService.search (current_user.id, q, category)
