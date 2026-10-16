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
from src.v1.api.acl.dtos.permission_transformer_dto import PermissionTransformerDto
from src.v1.api.acl.dtos.permission_validator_dto import (
    PermissionCreateValidatorDto,
    PermissionUpdateValidatorDto,
)
from src.v1.api.acl.services.permission_admin_service import PermissionAdminService
from src.v1.api.user.databases.models.user_model import User

permissionAdminRouter = APIRouter (prefix="/api/v1/admin/permissions", tags=["PermissionAdmin"])

@permissionAdminRouter.get (
    "/",
    status_code=Status.OK,
    dependencies=[rateLimit (times=10, seconds=60), Depends (security)],
    response_model=OffsetPagination[PermissionTransformerDto],
    responses=getPaginationResponses (unauthorized=True, forbidden=True),
)
async def index (
    current_user: User = Depends (requirePermission ("permission.view")),
    orders: Optional[str] = Query (None, description="Order by fields (e.g., 'created_at:desc,name:asc')"),
    filters: Optional[str] = Query (None, description="Filter by fields (e.g., 'q:user,guard_name:web')"),
    limitPage: Optional[int] = Query (10, ge=1, le=500),
    currentPage: Optional[int] = Query (1, ge=1),
) -> OffsetPagination[PermissionTransformerDto]:
    """
    Index
    """
    page = {"currentPage": currentPage or 1, "limitPage": limitPage or 10}
    return await PermissionAdminService.all (parseOrders (orders), parseFilters (filters), page)

@permissionAdminRouter.get (
    "/{id}",
    status_code=Status.OK,
    dependencies=[rateLimit (times=10, seconds=60), Depends (security)],
    response_model=PermissionTransformerDto,
    responses=getStandardResponses (unauthorized=True, forbidden=True, not_found=True),
)
async def show (
    id: str,
    current_user: User = Depends (requirePermission ("permission.view")),
) -> PermissionTransformerDto:
    """
    Show
    """
    return await PermissionAdminService.get (id)

@permissionAdminRouter.post (
    "/",
    status_code=Status.CREATED,
    dependencies=[rateLimit (times=10, seconds=60), Depends (security)],
    response_model=PermissionTransformerDto,
    responses=getStandardResponses (unauthorized=True, forbidden=True, bad_request=True, unvalidated=True),
)
async def store (
    dto: PermissionCreateValidatorDto = Body (
        ...,
        examples={
            "default": {
                "value": {
                    "name": "report.view",
                    "guard_name": "web",
                }
            }
        },
    ),
    current_user: User = Depends (requirePermission ("permission.create")),
) -> PermissionTransformerDto:
    """
    Store
    """
    return await PermissionAdminService.create (current_user.id, dto)

@permissionAdminRouter.put (
    "/{id}",
    status_code=Status.OK,
    dependencies=[rateLimit (times=10, seconds=60), Depends (security)],
    response_model=PermissionTransformerDto,
    responses=getStandardResponses (unauthorized=True, forbidden=True, bad_request=True, not_found=True, unvalidated=True),
)
async def update (
    id: str,
    dto: PermissionUpdateValidatorDto = Body (
        ...,
        examples={
            "default": {
                "value": {
                    "name": "report.view",
                    "guard_name": "web",
                }
            }
        },
    ),
    current_user: User = Depends (requirePermission ("permission.update")),
) -> PermissionTransformerDto:
    """
    Update
    """
    return await PermissionAdminService.update (current_user.id, id, dto)

@permissionAdminRouter.delete (
    "/{id}",
    status_code=Status.OK,
    dependencies=[rateLimit (times=10, seconds=60), Depends (security)],
    response_model=PermissionTransformerDto,
    responses=getStandardResponses (unauthorized=True, forbidden=True, not_found=True),
)
async def destroy (
    id: str,
    current_user: User = Depends (requirePermission ("permission.delete")),
) -> PermissionTransformerDto:
    """
    Destroy
    """
    return await PermissionAdminService.delete (current_user.id, id)

@permissionAdminRouter.post (
    "/import",
    status_code=Status.OK,
    dependencies=[rateLimit (times=10, seconds=60), Depends (security)],
    response_model=str,
    responses=getStandardResponses (unauthorized=True, forbidden=True, bad_request=True),
)
async def importPermissions (
    background_tasks: BackgroundTasks,
    file: UploadFile = File (...),
    current_user: User = Depends (requirePermission ("permission.import")),
) -> str:
    """
    Import Permissions
    """
    fileContent = await readImportUpload (file)
    return await PermissionAdminService.importPermissions (
        background_tasks,
        current_user.id,
        fileContent,
        file.filename or "permissions.csv",
    )

@permissionAdminRouter.post (
    "/export",
    status_code=Status.OK,
    dependencies=[rateLimit (times=10, seconds=60), Depends (security)],
    response_model=str,
    responses=getStandardResponses (unauthorized=True, forbidden=True),
)
async def exportPermissions (
    background_tasks: BackgroundTasks,
    export_type: Optional[str] = Query (default="csv", enum=["csv", "xlsx"]),
    orders: Optional[str] = Query (None, description="Same as the list (e.g., 'created_at:desc')"),
    filters: Optional[str] = Query (None, description="Same as the list (e.g., 'q:user,guard_name:web')"),
    current_user: User = Depends (requirePermission ("permission.export")),
) -> str:
    """
    Export Permissions
    """
    return await PermissionAdminService.exportPermissions (
        background_tasks,
        current_user.id,
        export_type or "csv",
        parseOrders (orders),
        parseFilters (filters),
    )
