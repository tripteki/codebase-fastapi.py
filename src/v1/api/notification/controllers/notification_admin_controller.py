from typing import Optional
from fastapi import APIRouter, Depends, Request, Query, status, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from fastapi_limiter.depends import RateLimiter
from src.app.bases.app_auth import AppAuth
from src.app.bases.app_i18n import AppI18n
from src.app.bases.app_security import security
from src.app.dtos.app_dto import Status, Description
from src.app.repositories.app_repository import OffsetPagination, OffsetPaginationType
from src.v1.api.notification.dtos.notification_transformer_dto import NotificationTransformerDto
from src.v1.api.notification.dtos.notification_validator_dto import NotificationIdentifierDto, NotificationCreateValidatorDto, NotificationUpdateValidatorDto
from src.v1.api.notification.services.notification_admin_service import NotificationAdminService
from src.v1.api.user.services.user_auth_service import UserAuthService

notificationAdminRouter = APIRouter (prefix="/api/v1/admin/notifications", tags=["NotificationAdmin"])

@notificationAdminRouter.get (
    "/",
    status_code=Status.OK,
    dependencies=[Depends (RateLimiter (times=10, seconds=60)), Depends (security)],
    response_model=OffsetPagination[NotificationTransformerDto],
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
                                "user_id": "string",
                                "type": "string",
                                "data": {},
                                "read_at": None,
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
async def index (request: Request, credentials: Optional[HTTPAuthorizationCredentials] = Depends (security), orders: Optional[str] = Query (None, description="Order by fields (e.g., 'created_at:desc,type:asc')"), filters: Optional[str] = Query (None, description="Filter by fields (e.g., 'type:info,user_id:123')"), limitPage: Optional[int] = Query (10, ge=1, le=100), currentPage: Optional[int] = Query (1, ge=1)) -> OffsetPagination[NotificationTransformerDto]:
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

    page = OffsetPaginationType (currentPage=currentPage or 1, limitPage=limitPage or 10)
    return await NotificationAdminService.all (userId, parsedOrders if parsedOrders else None, parsedFilters if parsedFilters else None, page)

@notificationAdminRouter.get (
    "/{id}",
    status_code=Status.OK,
    dependencies=[Depends (RateLimiter (times=10, seconds=60)), Depends (security)],
    response_model=NotificationTransformerDto,
    responses={
        200: {
            "description": Description.OK,
            "content": {
                "application/json": {
                    "example": {
                        "id": "string",
                        "user_id": "string",
                        "type": "string",
                        "data": {},
                        "read_at": None,
                        "created_at": "string",
                        "updated_at": "string",
                        "deleted_at": None
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
async def show (id: str, request: Request, credentials: Optional[HTTPAuthorizationCredentials] = Depends (security)) -> NotificationTransformerDto:
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
    return await NotificationAdminService.get (userId, id)

@notificationAdminRouter.delete (
    "/activate/{id}",
    status_code=Status.OK,
    dependencies=[Depends (RateLimiter (times=10, seconds=60)), Depends (security)],
    response_model=NotificationTransformerDto,
    responses={
        200: {
            "description": Description.OK,
            "content": {
                "application/json": {
                    "example": {
                        "id": "string",
                        "user_id": "string",
                        "type": "string",
                        "data": {},
                        "read_at": None,
                        "created_at": "string",
                        "updated_at": "string",
                        "deleted_at": None
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
async def activate (id: str, request: Request, credentials: Optional[HTTPAuthorizationCredentials] = Depends (security)) -> NotificationTransformerDto:
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
    return await NotificationAdminService.restore (userId, id)

@notificationAdminRouter.delete (
    "/deactivate/{id}",
    status_code=Status.OK,
    dependencies=[Depends (RateLimiter (times=10, seconds=60)), Depends (security)],
    response_model=NotificationTransformerDto,
    responses={
        200: {
            "description": Description.OK,
            "content": {
                "application/json": {
                    "example": {
                        "id": "string",
                        "user_id": "string",
                        "type": "string",
                        "data": {},
                        "read_at": None,
                        "created_at": "string",
                        "updated_at": "string",
                        "deleted_at": None
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
async def deactivate (id: str, request: Request, credentials: Optional[HTTPAuthorizationCredentials] = Depends (security)) -> NotificationTransformerDto:
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
    return await NotificationAdminService.delete (userId, id)
