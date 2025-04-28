from typing import Optional
from fastapi import (
    APIRouter,
    Body,
    Depends,
    File,
    HTTPException,
    Query,
    Request,
    Response,
    status,
    UploadFile,
)
from fastapi.security import HTTPAuthorizationCredentials
from fastapi_limiter.depends import RateLimiter
from src.app.bases.app_i18n import AppI18n
from src.app.bases.app_security import security
from src.app.dependencies.app_auth_api_dependency import get_current_user
from src.app.dtos.app_dto import Status, Description
from src.app.repositories.app_repository import OffsetPagination
from src.app.utils.app_query_parser import parseOrders, parseFilters
from src.app.utils.app_response_helper import getStandardResponses, getPaginationResponses
from src.v1.api.user.databases.models.user_model import User
from src.v1.api.user.services.user_auth_service import UserAuthService
from src.v1.api.user.dtos.user_transformer_dto import UserTransformerDto
from src.v1.api.user.dtos.user_validator_dto import (
    UserCreateValidatorDto,
    UserExportTypeDto,
    UserUpdateValidatorDto,
)
from src.v1.api.user.services.user_admin_service import UserAdminService
from src.v1.api.user.services.user_auth_service import UserAuthService

userAdminRouter = APIRouter (prefix="/api/v1/admin/users", tags=["UserAdmin"])

@userAdminRouter.get (
    "/",
    status_code=Status.OK,
    dependencies=[Depends (RateLimiter (times=10, seconds=60)), Depends (security)],
    response_model=OffsetPagination[UserTransformerDto],
    responses=getPaginationResponses (
        item_example={
            "id": "string",
            "name": "string",
            "email": "string",
            "email_verified_at": None,
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
    orders: Optional[str] = Query (None, description="Order by fields (e.g., 'created_at:desc,name:asc')"),
    filters: Optional[str] = Query (None, description="Filter by fields (e.g., 'name:john,email:test')"),
    limitPage: Optional[int] = Query (10, ge=1, le=100),
    currentPage: Optional[int] = Query (1, ge=1)
) -> OffsetPagination[UserTransformerDto]:
    """
    Index
    """
    page = {"currentPage": currentPage or 1, "limitPage": limitPage or 10}
    return await UserAdminService.all (current_user.id, parseOrders (orders), parseFilters (filters), page)

@userAdminRouter.delete (
    "/activate/{id}",
    status_code=Status.OK,
    dependencies=[Depends (RateLimiter (times=10, seconds=60)), Depends (security)],
    response_model=UserTransformerDto,
    responses=getStandardResponses (unauthorized=True, forbidden=True, not_found=True)
)
async def activate (
    id: str,
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends (security)
) -> UserTransformerDto:
    """
    Activate
    """
    i18n = AppI18n.i18n ()
    token = UserAuthService.httpBearerToken (request)
    if not token:
        raise HTTPException (status_code=status.HTTP_401_UNAUTHORIZED, detail=i18n.t ("_v1_user.auth.missing_token"))
    userId = await UserAuthService.validateToken (token)
    if not userId:
        raise HTTPException (status_code=status.HTTP_401_UNAUTHORIZED, detail=i18n.t ("_v1_user.auth.invalid_token"))
    return await UserAdminService.restore (userId, id)

@userAdminRouter.delete (
    "/deactivate/{id}",
    status_code=Status.OK,
    dependencies=[Depends (RateLimiter (times=10, seconds=60)), Depends (security)],
    response_model=UserTransformerDto,
    responses=getStandardResponses (unauthorized=True, forbidden=True, not_found=True)
)
async def deactivate (
    id: str,
    current_user: User = Depends (get_current_user)
) -> UserTransformerDto:
    """
    Deactivate
    """
    return await UserAdminService.delete (current_user.id, id)

@userAdminRouter.get (
    "/{id}",
    status_code=Status.OK,
    dependencies=[Depends (RateLimiter (times=10, seconds=60)), Depends (security)],
    response_model=UserTransformerDto,
    responses=getStandardResponses (unauthorized=True, forbidden=True, not_found=True)
)
async def show (
    id: str,
    current_user: User = Depends (get_current_user)
) -> UserTransformerDto:
    """
    Show
    """
    return await UserAdminService.get (current_user.id, id)

@userAdminRouter.put (
    "/{id}",
    status_code=Status.OK,
    dependencies=[Depends (RateLimiter (times=10, seconds=60)), Depends (security)],
    response_model=UserTransformerDto,
    responses=getStandardResponses (unauthorized=True, forbidden=True, bad_request=True, not_found=True, unvalidated=True)
)
async def update (
    id: str,
    dto: UserUpdateValidatorDto = Body (..., examples={"name": "user", "email": "user@mail.com", "password": "12345678", "password_confirmation": "12345678"}),
    current_user: User = Depends (get_current_user)
) -> UserTransformerDto:
    """
    Update
    """
    return await UserAdminService.update (current_user.id, id, dto)

@userAdminRouter.post (
    "/",
    status_code=Status.CREATED,
    dependencies=[Depends (RateLimiter (times=10, seconds=60)), Depends (security)],
    response_model=UserTransformerDto,
    responses=getStandardResponses (unauthorized=True, forbidden=True, bad_request=True, unvalidated=True)
)
async def store (
    dto: UserCreateValidatorDto = Body (..., examples={"name": "user", "email": "user@mail.com", "password": "12345678", "password_confirmation": "12345678"}),
    current_user: User = Depends (get_current_user)
) -> UserTransformerDto:
    """
    Store
    """
    return await UserAdminService.create (current_user.id, dto)

@userAdminRouter.put (
    "/verify/{id}",
    status_code=Status.OK,
    dependencies=[Depends (RateLimiter (times=10, seconds=60)), Depends (security)],
    response_model=UserTransformerDto,
    responses=getStandardResponses (unauthorized=True, forbidden=True, bad_request=True, not_found=True)
)
async def verify (
    id: str,
    current_user: User = Depends (get_current_user)
) -> UserTransformerDto:
    """
    Verify
    """
    return await UserAdminService.verify (current_user.id, id)

@userAdminRouter.post (
    "/import",
    status_code=Status.OK,
    dependencies=[Depends (RateLimiter (times=10, seconds=60)), Depends (security)],
    response_model=str,
    summary="Import Users from File",
    description="""
Import multiple users from CSV, XLSX, or XLS file.

**Supported File Formats:**
- CSV (.csv)
- Excel (.xlsx)
- Excel 97-2003 (.xls)

**Required Columns:**
- `name`
- `email`
- `password`

**CSV Example:**
```csv
name,email,password
John Doe,john@example.com,password123
Jane Smith,jane@example.com,securepass456
Bob Wilson,bob@example.com,mypassword789
```

**Excel Example:**
| name | email | password |
|------|-------|----------|
| John Doe | john@example.com | password123 |
| Jane Smith | jane@example.com | securepass456 |

**Notes:**
- Duplicate emails will be skipped
- Empty rows will be skipped
- Import is processed asynchronously
- You will receive a notification when import is complete
    """,
    responses=getStandardResponses (
        success=True,
        success_desc=Description.IMPORT_STARTED,
        success_example="string",
        unauthorized=True,
        forbidden=True,
        bad_request=True,
        unauthorized_desc=Description.UNAUTHORIZED_MISSING_TOKEN,
        forbidden_desc=Description.FORBIDDEN_INSUFFICIENT_PERMISSIONS
    )
)
async def import_users (
    file: UploadFile = File (..., description="Upload CSV, XLSX, or XLS file containing user data with columns: name, email, password"),
    current_user: User = Depends (get_current_user)
) -> str:
    """
    Import Users from File

    Upload a file containing user data to import multiple users at once.
    The file will be processed asynchronously in the background.
    """
    try:
        fileContent = await file.read ()
        return await UserAdminService.import_users (current_user.id, fileContent, file.filename)
    except HTTPException:
        raise
    except Exception as e:
        i18n = AppI18n.i18n ()
        raise HTTPException (status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=i18n.t ("_v1_user.admin.internal_server_error"))

@userAdminRouter.post (
    "/export",
    status_code=Status.OK,
    dependencies=[Depends (RateLimiter (times=10, seconds=60)), Depends (security)],
    response_model=str,
    summary="Export Users to File",
    description="""
Export all active users to CSV, XLSX, or XLS file.

**Supported Export Formats:**
- CSV (.csv)
- Excel (.xlsx)
- Excel 97-2003 (.xls)

**Exported Data Includes:**
- User ID
- Name
- Email
- Email Verified At
- Created At
- Updated At

**Process:**
1. Request export with desired format
2. Export is processed asynchronously in the background
3. Receive notification when export is ready
4. Download file from notification link

**Example Output (CSV):**
```csv
id,name,email,email_verified_at,created_at,updated_at
01KEF...,John Doe,john@example.com,2026-01-09T10:30:00,2026-01-08T15:20:00,2026-01-09T10:30:00
01KEG...,Jane Smith,jane@example.com,2026-01-09T11:15:00,2026-01-08T16:45:00,2026-01-09T11:15:00
```
    """,
    responses=getStandardResponses (
        success=True,
        success_desc=Description.EXPORT_STARTED,
        success_example="string",
        unauthorized=True,
        forbidden=True,
        unauthorized_desc=Description.UNAUTHORIZED_MISSING_TOKEN,
        forbidden_desc=Description.FORBIDDEN_INSUFFICIENT_PERMISSIONS
    )
)
async def export_users (
    export_type: Optional[str] = Query (default="csv", description="File format: csv (default), xlsx, or xls", enum=["csv", "xls", "xlsx"]),
    current_user: User = Depends (get_current_user)
) -> str:
    """
    Export Users to File

    Export all active users to the specified file format.
    The export will be processed asynchronously and you will receive a notification with the download link.
    """
    try:
        return await UserAdminService.export_users (current_user.id, export_type)
    except HTTPException:
        raise
    except Exception as e:
        i18n = AppI18n.i18n ()
        raise HTTPException (status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=i18n.t ("_v1_user.admin.internal_server_error"))
