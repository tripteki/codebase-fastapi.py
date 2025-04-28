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
from src.app.bases.app_auth import AppAuth
from src.app.bases.app_i18n import AppI18n
from src.app.bases.app_security import security
from src.app.dtos.app_dto import Status, Description
from src.app.repositories.app_repository import OffsetPagination
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
    responses={
        200: {
            "description": Description.OK,
            "content": {
                "application/json": {
                    "example": {
                        "totalPage": 0,
                        "perPage": 0,
                        "currentPage": 0,
                        "nextPage": 0,
                        "previousPage": 0,
                        "firstPage": 0,
                        "lastPage": 0,
                        "data": [
                            {
                                "id": "string",
                                "name": "string",
                                "email": "string",
                                "email_verified_at": None,
                                "created_at": "string",
                                "updated_at": "string",
                                "deleted_at": None
                            }
                        ]
                    }
                }
            }
        },
        401: {
            "description": Description.UNAUTHORIZED,
            "content": {
                "application/json": {
                    "example": {
                        "detail": "string"
                    }
                }
            }
        },
        403: {
            "description": Description.FORBIDDEN,
            "content": {
                "application/json": {
                    "example": {
                        "detail": "string"
                    }
                }
            }
        }
    }
)
async def index (request: Request, credentials: Optional[HTTPAuthorizationCredentials] = Depends (security), orders: Optional[str] = Query (None, description="Order by fields (e.g., 'created_at:desc,name:asc')"), filters: Optional[str] = Query (None, description="Filter by fields (e.g., 'name:john,email:test')"), limitPage: Optional[int] = Query (10, ge=1, le=100), currentPage: Optional[int] = Query (1, ge=1)) -> OffsetPagination[UserTransformerDto]:
    """
    Index
    """
    i18n = AppI18n.i18n ()
    token = UserAuthService.httpBearerToken (request)
    if not token:
        raise HTTPException (status_code=status.HTTP_401_UNAUTHORIZED, detail=i18n.t ("_v1_user.auth.missing_token"))
    userId = await UserAuthService.validateToken (token)
    if not userId:
        raise HTTPException (status_code=status.HTTP_401_UNAUTHORIZED, detail=i18n.t ("_v1_user.auth.invalid_token"))

    parsedOrders = []
    if orders:
        for order in orders.split (","):
            parts = order.split (":")
            if len (parts) == 2:
                parsedOrders.append ({"field": parts[0].strip (), "direction": parts[1].strip ()})

    parsedFilters = []
    if filters:
        for filter_item in filters.split (","):
            parts = filter_item.split (":")
            if len (parts) == 2:
                parsedFilters.append ({"field": parts[0].strip (), "search": parts[1].strip ()})

    page = {"currentPage": currentPage or 1, "limitPage": limitPage or 10}
    return await UserAdminService.all (userId, parsedOrders if parsedOrders else None, parsedFilters if parsedFilters else None, page)

@userAdminRouter.get (
    "/{id}",
    status_code=Status.OK,
    dependencies=[Depends (RateLimiter (times=10, seconds=60)), Depends (security)],
    response_model=UserTransformerDto,
    responses={
        200: {
            "description": Description.OK,
            "content": {
                "application/json": {
                    "example": {
                        "id": "string",
                        "name": "string",
                        "email": "string",
                        "email_verified_at": None,
                        "created_at": "string",
                        "updated_at": "string"
                    }
                }
            }
        },
        401: {
            "description": Description.UNAUTHORIZED,
            "content": {
                "application/json": {
                    "example": {
                        "detail": "string"
                    }
                }
            }
        },
        403: {
            "description": Description.FORBIDDEN,
            "content": {
                "application/json": {
                    "example": {
                        "detail": "string"
                    }
                }
            }
        },
        404: {
            "description": Description.NOT_FOUND,
            "content": {
                "application/json": {
                    "example": {
                        "detail": "string"
                    }
                }
            }
        }
    }
)
async def show (id: str, request: Request, credentials: Optional[HTTPAuthorizationCredentials] = Depends (security)) -> UserTransformerDto:
    """
    Show
    """
    i18n = AppI18n.i18n ()
    token = UserAuthService.httpBearerToken (request)
    if not token:
        raise HTTPException (status_code=status.HTTP_401_UNAUTHORIZED, detail=i18n.t ("_v1_user.auth.missing_token"))
    userId = await UserAuthService.validateToken (token)
    if not userId:
        raise HTTPException (status_code=status.HTTP_401_UNAUTHORIZED, detail=i18n.t ("_v1_user.auth.invalid_token"))
    return await UserAdminService.get (userId, id)

@userAdminRouter.put (
    "/{id}",
    status_code=Status.OK,
    dependencies=[Depends (RateLimiter (times=10, seconds=60)), Depends (security)],
    response_model=UserTransformerDto,
    responses={
        200: {
            "description": Description.OK,
            "content": {
                "application/json": {
                    "example": {
                        "id": "string",
                        "name": "string",
                        "email": "string",
                        "email_verified_at": None,
                        "created_at": "string",
                        "updated_at": "string"
                    }
                }
            }
        },
        400: {
            "description": Description.BAD_REQUEST,
            "content": {
                "application/json": {
                    "example": {
                        "detail": "string"
                    }
                }
            }
        },
        401: {
            "description": Description.UNAUTHORIZED,
            "content": {
                "application/json": {
                    "example": {
                        "detail": "string"
                    }
                }
            }
        },
        403: {
            "description": Description.FORBIDDEN,
            "content": {
                "application/json": {
                    "example": {
                        "detail": "string"
                    }
                }
            }
        },
        404: {
            "description": Description.NOT_FOUND,
            "content": {
                "application/json": {
                    "example": {
                        "detail": "string"
                    }
                }
            }
        },
        422: {
            "description": Description.UNVALIDATED,
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "type": "value_error",
                                "loc": ["body"],
                                "msg": "string",
                                "input": {
                                    "name": "string",
                                    "email": "string",
                                    "password": "string",
                                    "password_confirmation": "string"
                                },
                                "ctx": {
                                    "error": "string"
                                }
                            }
                        ]
                    }
                }
            }
        }
    }
)
async def update (id: str, dto: UserUpdateValidatorDto = Body (..., examples={"name": "user", "email": "user@mail.com", "password": "12345678", "password_confirmation": "12345678"}), request: Request = None, credentials: Optional[HTTPAuthorizationCredentials] = Depends (security)) -> UserTransformerDto:
    """
    Update
    """
    i18n = AppI18n.i18n ()
    token = UserAuthService.httpBearerToken (request)
    if not token:
        raise HTTPException (status_code=status.HTTP_401_UNAUTHORIZED, detail=i18n.t ("_v1_user.auth.missing_token"))
    userId = await UserAuthService.validateToken (token)
    if not userId:
        raise HTTPException (status_code=status.HTTP_401_UNAUTHORIZED, detail=i18n.t ("_v1_user.auth.invalid_token"))
    return await UserAdminService.update (userId, id, dto)

@userAdminRouter.post (
    "/",
    status_code=Status.CREATED,
    dependencies=[Depends (RateLimiter (times=10, seconds=60)), Depends (security)],
    response_model=UserTransformerDto,
    responses={
        201: {
            "description": Description.CREATED,
            "content": {
                "application/json": {
                    "example": {
                        "id": "string",
                        "name": "string",
                        "email": "string",
                        "email_verified_at": None,
                        "created_at": "string",
                        "updated_at": "string"
                    }
                }
            }
        },
        400: {
            "description": Description.BAD_REQUEST,
            "content": {
                "application/json": {
                    "example": {
                        "detail": "string"
                    }
                }
            }
        },
        401: {
            "description": Description.UNAUTHORIZED,
            "content": {
                "application/json": {
                    "example": {
                        "detail": "string"
                    }
                }
            }
        },
        403: {
            "description": Description.FORBIDDEN,
            "content": {
                "application/json": {
                    "example": {
                        "detail": "string"
                    }
                }
            }
        },
        422: {
            "description": Description.UNVALIDATED,
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "type": "value_error",
                                "loc": ["body"],
                                "msg": "string",
                                "input": {
                                    "name": "string",
                                    "email": "string",
                                    "password": "string",
                                    "password_confirmation": "string"
                                },
                                "ctx": {
                                    "error": "string"
                                }
                            }
                        ]
                    }
                }
            }
        }
    }
)
async def store (dto: UserCreateValidatorDto = Body (..., examples={"name": "user", "email": "user@mail.com", "password": "12345678", "password_confirmation": "12345678"}), request: Request = None, credentials: Optional[HTTPAuthorizationCredentials] = Depends (security)) -> UserTransformerDto:
    """
    Store
    """
    i18n = AppI18n.i18n ()
    token = UserAuthService.httpBearerToken (request)
    if not token:
        raise HTTPException (status_code=status.HTTP_401_UNAUTHORIZED, detail=i18n.t ("_v1_user.auth.missing_token"))
    userId = await UserAuthService.validateToken (token)
    if not userId:
        raise HTTPException (status_code=status.HTTP_401_UNAUTHORIZED, detail=i18n.t ("_v1_user.auth.invalid_token"))
    return await UserAdminService.create (userId, dto)

@userAdminRouter.delete (
    "/activate/{id}",
    status_code=Status.OK,
    dependencies=[Depends (RateLimiter (times=10, seconds=60)), Depends (security)],
    response_model=UserTransformerDto,
    responses={
        200: {
            "description": Description.OK,
            "content": {
                "application/json": {
                    "example": {
                        "id": "string",
                        "name": "string",
                        "email": "string",
                        "email_verified_at": None,
                        "created_at": "string",
                        "updated_at": "string"
                    }
                }
            }
        },
        401: {
            "description": Description.UNAUTHORIZED,
            "content": {
                "application/json": {
                    "example": {
                        "detail": "string"
                    }
                }
            }
        },
        403: {
            "description": Description.FORBIDDEN,
            "content": {
                "application/json": {
                    "example": {
                        "detail": "string"
                    }
                }
            }
        },
        404: {
            "description": Description.NOT_FOUND,
            "content": {
                "application/json": {
                    "example": {
                        "detail": "string"
                    }
                }
            }
        }
    }
)
async def activate (id: str, request: Request, credentials: Optional[HTTPAuthorizationCredentials] = Depends (security)) -> UserTransformerDto:
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
    responses={
        200: {
            "description": Description.OK,
            "content": {
                "application/json": {
                    "example": {
                        "id": "string",
                        "name": "string",
                        "email": "string",
                        "email_verified_at": None,
                        "created_at": "string",
                        "updated_at": "string"
                    }
                }
            }
        },
        401: {
            "description": Description.UNAUTHORIZED,
            "content": {
                "application/json": {
                    "example": {
                        "detail": "string"
                    }
                }
            }
        },
        403: {
            "description": Description.FORBIDDEN,
            "content": {
                "application/json": {
                    "example": {
                        "detail": "string"
                    }
                }
            }
        },
        404: {
            "description": Description.NOT_FOUND,
            "content": {
                "application/json": {
                    "example": {
                        "detail": "string"
                    }
                }
            }
        }
    }
)
async def deactivate (id: str, request: Request, credentials: Optional[HTTPAuthorizationCredentials] = Depends (security)) -> UserTransformerDto:
    """
    Deactivate
    """
    i18n = AppI18n.i18n ()
    token = UserAuthService.httpBearerToken (request)
    if not token:
        raise HTTPException (status_code=status.HTTP_401_UNAUTHORIZED, detail=i18n.t ("_v1_user.auth.missing_token"))
    userId = await UserAuthService.validateToken (token)
    if not userId:
        raise HTTPException (status_code=status.HTTP_401_UNAUTHORIZED, detail=i18n.t ("_v1_user.auth.invalid_token"))
    return await UserAdminService.delete (userId, id)

@userAdminRouter.put (
    "/verify/{id}",
    status_code=Status.OK,
    dependencies=[Depends (RateLimiter (times=10, seconds=60)), Depends (security)],
    response_model=UserTransformerDto,
    responses={
        200: {
            "description": Description.OK,
            "content": {
                "application/json": {
                    "example": {
                        "id": "string",
                        "name": "string",
                        "email": "string",
                        "email_verified_at": None,
                        "created_at": "string",
                        "updated_at": "string"
                    }
                }
            }
        },
        400: {
            "description": Description.BAD_REQUEST,
            "content": {
                "application/json": {
                    "example": {
                        "detail": "string"
                    }
                }
            }
        },
        401: {
            "description": Description.UNAUTHORIZED,
            "content": {
                "application/json": {
                    "example": {
                        "detail": "string"
                    }
                }
            }
        },
        403: {
            "description": Description.FORBIDDEN,
            "content": {
                "application/json": {
                    "example": {
                        "detail": "string"
                    }
                }
            }
        },
        404: {
            "description": Description.NOT_FOUND,
            "content": {
                "application/json": {
                    "example": {
                        "detail": "string"
                    }
                }
            }
        }
    }
)
async def verify (id: str, request: Request, credentials: Optional[HTTPAuthorizationCredentials] = Depends (security)) -> UserTransformerDto:
    """
    Verify
    """
    i18n = AppI18n.i18n ()
    token = UserAuthService.httpBearerToken (request)
    if not token:
        raise HTTPException (status_code=status.HTTP_401_UNAUTHORIZED, detail=i18n.t ("_v1_user.auth.missing_token"))
    userId = await UserAuthService.validateToken (token)
    if not userId:
        raise HTTPException (status_code=status.HTTP_401_UNAUTHORIZED, detail=i18n.t ("_v1_user.auth.invalid_token"))
    return await UserAdminService.verify (userId, id)

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
    responses={
        200: {
            "description": Description.IMPORT_STARTED,
            "content": {
                "application/json": {
                    "example": "string"
                }
            }
        },
        400: {
            "description": Description.BAD_REQUEST,
            "content": {
                "application/json": {
                    "example": {
                        "detail": "string"
                    }
                }
            }
        },
        401: {
            "description": Description.UNAUTHORIZED_MISSING_TOKEN,
            "content": {
                "application/json": {
                    "example": {
                        "detail": "string"
                    }
                }
            }
        },
        403: {
            "description": Description.FORBIDDEN_INSUFFICIENT_PERMISSIONS,
            "content": {
                "application/json": {
                    "example": {
                        "detail": "string"
                    }
                }
            }
        }
    }
)
async def import_users (request: Request, credentials: Optional[HTTPAuthorizationCredentials] = Depends (security), file: UploadFile = File (..., description="Upload CSV, XLSX, or XLS file containing user data with columns: name, email, password")) -> str:
    """
    Import Users from File

    Upload a file containing user data to import multiple users at once.
    The file will be processed asynchronously in the background.
    """
    i18n = AppI18n.i18n ()
    token = UserAuthService.httpBearerToken (request)
    if not token:
        raise HTTPException (status_code=status.HTTP_401_UNAUTHORIZED, detail=i18n.t ("_v1_user.auth.missing_token"))
    try:
        userId = await UserAuthService.validateToken (token)
        if not userId:
            raise HTTPException (status_code=status.HTTP_401_UNAUTHORIZED, detail=i18n.t ("_v1_user.auth.invalid_token"))
        fileContent = await file.read ()
        return await UserAdminService.import_users (userId, fileContent, file.filename)
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
    responses={
        200: {
            "description": Description.EXPORT_STARTED,
            "content": {
                "application/json": {
                    "example": "string"
                }
            }
        },
        401: {
            "description": Description.UNAUTHORIZED_MISSING_TOKEN,
            "content": {
                "application/json": {
                    "example": {
                        "detail": "string"
                    }
                }
            }
        },
        403: {
            "description": Description.FORBIDDEN_INSUFFICIENT_PERMISSIONS,
            "content": {
                "application/json": {
                    "example": {
                        "detail": "string"
                    }
                }
            }
        }
    }
)

async def export_users (export_type: Optional[str] = Query (default="csv", description="File format: csv (default), xlsx, or xls", enum=["csv", "xls", "xlsx"]), request: Request = None, credentials: Optional[HTTPAuthorizationCredentials] = Depends (security)) -> str:
    """
    Export Users to File

    Export all active users to the specified file format.
    The export will be processed asynchronously and you will receive a notification with the download link.
    """
    i18n = AppI18n.i18n ()
    token = UserAuthService.httpBearerToken (request)
    if not token:
        raise HTTPException (status_code=status.HTTP_401_UNAUTHORIZED, detail=i18n.t ("_v1_user.auth.missing_token"))
    try:
        userId = await UserAuthService.validateToken (token)
        if not userId:
            raise HTTPException (status_code=status.HTTP_401_UNAUTHORIZED, detail=i18n.t ("_v1_user.auth.invalid_token"))
        return await UserAdminService.export_users (userId, export_type)
    except HTTPException:
        raise
    except Exception as e:
        i18n = AppI18n.i18n ()
        raise HTTPException (status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=i18n.t ("_v1_user.admin.internal_server_error"))
