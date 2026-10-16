from typing import Optional
from fastapi import APIRouter, BackgroundTasks, Body, Depends, File, Query, UploadFile
from src.app.bases.app_security import security
from src.app.dependencies.app_permission_dependency import requirePermission
from src.app.dependencies.app_rate_limit import rateLimit
from src.app.dtos.app_dto import Status
from src.app.repositories.app_repository import OffsetPagination
from src.app.utils.app_query_parser import parseFilters, parseOrders
from src.app.utils.app_response_helper import getPaginationResponses, getStandardResponses
from src.app.utils.app_upload_guard import readImportUpload
from src.v1.api.acl.dtos.role_transformer_dto import RoleTransformerDto
from src.v1.api.acl.dtos.role_validator_dto import RoleCreateValidatorDto, RoleUpdateValidatorDto
from src.v1.api.acl.services.role_admin_service import RoleAdminService
from src.v1.api.user.databases.models.user_model import User

roleAdminRouter = APIRouter (prefix="/api/v1/admin/roles", tags=["RoleAdmin"])

@roleAdminRouter.get (
    "/",
    status_code=Status.OK,
    dependencies=[rateLimit (times=10, seconds=60), Depends (security)],
    response_model=OffsetPagination[RoleTransformerDto],
    responses=getPaginationResponses (unauthorized=True, forbidden=True),
)
async def index (
    current_user: User = Depends (requirePermission ("role.view")),
    orders: Optional[str] = Query (None, description="Order by fields (e.g., 'created_at:desc,name:asc')"),
    filters: Optional[str] = Query (None, description="Filter by fields (e.g., 'q:admin,guard_name:web')"),
    limitPage: Optional[int] = Query (10, ge=1, le=100),
    currentPage: Optional[int] = Query (1, ge=1),
) -> OffsetPagination[RoleTransformerDto]:
    """
    Index
    """
    page = {"currentPage": currentPage or 1, "limitPage": limitPage or 10}
    return await RoleAdminService.all (parseOrders (orders), parseFilters (filters), page)

@roleAdminRouter.get (
    "/{id}",
    status_code=Status.OK,
    dependencies=[rateLimit (times=10, seconds=60), Depends (security)],
    response_model=RoleTransformerDto,
    responses=getStandardResponses (unauthorized=True, forbidden=True, not_found=True),
)
async def show (
    id: str,
    current_user: User = Depends (requirePermission ("role.view")),
) -> RoleTransformerDto:
    """
    Show
    """
    return await RoleAdminService.get (id)

@roleAdminRouter.post (
    "/",
    status_code=Status.CREATED,
    dependencies=[rateLimit (times=10, seconds=60), Depends (security)],
    response_model=RoleTransformerDto,
    responses=getStandardResponses (unauthorized=True, forbidden=True, bad_request=True, unvalidated=True),
)
async def store (
    dto: RoleCreateValidatorDto = Body (
        ...,
        examples={
            "default": {
                "value": {
                    "name": "analyst",
                    "guard_name": "web",
                    "permission_ids": [],
                }
            }
        },
    ),
    current_user: User = Depends (requirePermission ("role.create")),
) -> RoleTransformerDto:
    """
    Store
    """
    return await RoleAdminService.create (current_user.id, dto)

@roleAdminRouter.put (
    "/{id}",
    status_code=Status.OK,
    dependencies=[rateLimit (times=10, seconds=60), Depends (security)],
    response_model=RoleTransformerDto,
    responses=getStandardResponses (unauthorized=True, forbidden=True, bad_request=True, not_found=True, unvalidated=True),
)
async def update (
    id: str,
    dto: RoleUpdateValidatorDto = Body (
        ...,
        examples={
            "default": {
                "value": {
                    "name": "analyst",
                    "guard_name": "web",
                    "permission_ids": [],
                }
            }
        },
    ),
    current_user: User = Depends (requirePermission ("role.update")),
) -> RoleTransformerDto:
    """
    Update
    """
    return await RoleAdminService.update (current_user.id, id, dto)

@roleAdminRouter.delete (
    "/{id}",
    status_code=Status.OK,
    dependencies=[rateLimit (times=10, seconds=60), Depends (security)],
    response_model=RoleTransformerDto,
    responses=getStandardResponses (unauthorized=True, forbidden=True, not_found=True),
)
async def destroy (
    id: str,
    current_user: User = Depends (requirePermission ("role.delete")),
) -> RoleTransformerDto:
    """
    Destroy
    """
    return await RoleAdminService.delete (current_user.id, id)

@roleAdminRouter.post (
    "/import",
    status_code=Status.OK,
    dependencies=[rateLimit (times=10, seconds=60), Depends (security)],
    response_model=str,
    responses=getStandardResponses (unauthorized=True, forbidden=True, bad_request=True),
)
async def importRoles (
    background_tasks: BackgroundTasks,
    file: UploadFile = File (...),
    current_user: User = Depends (requirePermission ("role.import")),
) -> str:
    """
    Import Roles
    """
    fileContent = await readImportUpload (file)
    return await RoleAdminService.importRoles (
        background_tasks,
        current_user.id,
        fileContent,
        file.filename or "roles.csv",
    )

@roleAdminRouter.post (
    "/export",
    status_code=Status.OK,
    dependencies=[rateLimit (times=10, seconds=60), Depends (security)],
    response_model=str,
    responses=getStandardResponses (unauthorized=True, forbidden=True),
)
async def exportRoles (
    background_tasks: BackgroundTasks,
    export_type: Optional[str] = Query (default="csv", enum=["csv", "xlsx"]),
    orders: Optional[str] = Query (None, description="Same as the list (e.g., 'created_at:desc')"),
    filters: Optional[str] = Query (None, description="Same as the list (e.g., 'q:admin,guard_name:web')"),
    current_user: User = Depends (requirePermission ("role.export")),
) -> str:
    """
    Export Roles
    """
    return await RoleAdminService.exportRoles (
        background_tasks,
        current_user.id,
        export_type or "csv",
        parseOrders (orders),
        parseFilters (filters),
    )
