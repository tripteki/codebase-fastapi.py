from typing import Optional
import logging
from fastapi import APIRouter, Body, Depends, HTTPException, Query, Request, Response, status
from fastapi.security import HTTPAuthorizationCredentials
from fastapi_limiter.depends import RateLimiter
from src.app.bases.app_auth import AppAuth
from src.app.bases.app_i18n import AppI18n
from src.app.bases.app_security import security
from src.app.dependencies.app_url_guard import urlGuard
from src.app.dtos.app_dto import Status, Description
from src.v1.api.user.dtos.user_transformer_dto import UserAuthTransformerDto, UserTransformerDto
from src.v1.api.user.dtos.user_validator_dto import (
    UserAuthDto,
    UserCreateValidatorDto,
    UserIdentifierEmailDto,
    UserResetterUpdateValidatorDto,
)
from src.v1.api.user.services.user_auth_service import UserAuthService

userAuthRouter = APIRouter (prefix="/api/v1/auth", tags=["UserAuth"])

@userAuthRouter.post (
    "/login",
    status_code=Status.CREATED,
    dependencies=[Depends (RateLimiter (times=3, seconds=60))],
    response_model=UserAuthTransformerDto,
    responses={
        201: {
            "description": Description.CREATED,
            "content": {
                "application/json": {
                    "example": {
                        "accessTokenTtl": 0,
                        "refreshTokenTtl": 0,
                        "accessToken": "string",
                        "refreshToken": "string"
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
                                    "identifierKey": "string",
                                    "identifierValue": "string",
                                    "password": "string"
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
async def login (
    dto: UserAuthDto = Body (...,
        examples={
            "default": {
                "value": {
                    "identifierKey": "email",
                    "identifierValue": "user@mail.com",
                    "password": "12345678",
                }
            }
        },
    ),
) -> UserAuthTransformerDto:
    """
    Login
    """
    return await UserAuthService.login (dto)

@userAuthRouter.post (
    "/logout",
    status_code=Status.OK,
    dependencies=[Depends (RateLimiter (times=10, seconds=60)), Depends (security)],
    response_model=bool,
    responses={
        200: {
            "description": Description.OK,
            "content": {
                "application/json": {
                    "example": True
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
async def logout (
    request: Request, credentials: Optional[HTTPAuthorizationCredentials] = Depends (security)
) -> bool:
    """
    Logout
    """
    i18n = AppI18n.i18n ()
    token = UserAuthService.httpBearerToken (request)
    if not token:
        raise HTTPException (
            status_code=status.HTTP_401_UNAUTHORIZED, detail=i18n.t ("_v1_user.auth.missing_token")
        )
    try:
        userId = await UserAuthService.validateToken (token)
        if not userId:
            raise HTTPException (
                status_code=status.HTTP_401_UNAUTHORIZED, detail=i18n.t ("_v1_user.auth.invalid_token")
            )
        result = await UserAuthService.logout (userId, token)
        return bool (result)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException (
            status_code=status.HTTP_401_UNAUTHORIZED, detail=i18n.t ("_v1_user.auth.invalid_token")
        )

@userAuthRouter.put (
    "/refresh",
    status_code=Status.OK,
    dependencies=[Depends (RateLimiter (times=3, seconds=60)), Depends (security)],
    response_model=UserAuthTransformerDto,
    responses={
        200: {
            "description": Description.OK,
            "content": {
                "application/json": {
                    "example": {
                        "accessTokenTtl": 0,
                        "refreshTokenTtl": 0,
                        "accessToken": "string",
                        "refreshToken": "string"
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
async def refresh (
    request: Request, credentials: Optional[HTTPAuthorizationCredentials] = Depends (security)
) -> UserAuthTransformerDto:
    """
    Refresh Token
    """
    i18n = AppI18n.i18n ()
    refreshToken = UserAuthService.httpBearerToken (request)
    if not refreshToken:
        raise HTTPException (
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=i18n.t ("_v1_user.auth.missing_refresh_token"),
        )
    return await UserAuthService.refresh (refreshToken)

@userAuthRouter.get (
    "/me",
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
        }
    }
)
async def me (
    request: Request, credentials: Optional[HTTPAuthorizationCredentials] = Depends (security)
) -> UserTransformerDto:
    """
    Get Current User
    """
    i18n = AppI18n.i18n ()
    token = UserAuthService.httpBearerToken (request)
    if not token:
        raise HTTPException (
            status_code=status.HTTP_401_UNAUTHORIZED, detail=i18n.t ("_v1_user.auth.missing_token")
        )
    try:
        userId = await UserAuthService.validateToken (token)
        if not userId:
            raise HTTPException (
                status_code=status.HTTP_401_UNAUTHORIZED, detail=i18n.t ("_v1_user.auth.invalid_token")
            )
        return await UserAuthService.me (userId)
    except Exception:
        raise HTTPException (
            status_code=status.HTTP_401_UNAUTHORIZED, detail=i18n.t ("_v1_user.auth.invalid_token")
        )

@userAuthRouter.post (
    "/register",
    status_code=Status.CREATED,
    dependencies=[Depends (RateLimiter (times=5, seconds=60))],
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
                        "updated_at": "string",
                        "deleted_at": None
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
async def register (
    dto: UserCreateValidatorDto = Body (
        ...,
        examples={
            "default": {
                "value": {
                    "name": "user",
                    "email": "user@mail.com",
                    "password": "12345678",
                    "password_confirmation": "12345678",
                }
            }
        },
    ),
) -> UserTransformerDto:
    """
    Register
    """
    return await UserAuthService.register (dto)

userAuthPublicRouter = APIRouter (prefix="/api/v1/auth", tags=["UserAuth"])

@userAuthPublicRouter.post (
    "/verify-email/{email}",
    status_code=Status.OK,
    dependencies=[Depends (RateLimiter (times=10, seconds=60)), Depends (urlGuard)],
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
                        "email_verified_at": "string",
                        "created_at": "string",
                        "updated_at": "string"
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
async def verify (email: str, signed: str = Query (..., description="The signed token")) -> UserTransformerDto:
    """
    Verify Email
    """
    return await UserAuthService.verify (email, signed)

@userAuthRouter.post (
    "/email/verification-notification",
    status_code=Status.OK,
    dependencies=[Depends (RateLimiter (times=3, seconds=60)), Depends (security)],
    response_model=str,
    responses={
        200: {
            "description": Description.OK,
            "content": {
                "application/json": {
                    "example": "string"
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
async def reverify (
    request: Request, credentials: Optional[HTTPAuthorizationCredentials] = Depends (security)
) -> str:
    """
    Resend Email Verification
    """
    i18n = AppI18n.i18n ()
    token = UserAuthService.httpBearerToken (request)
    if not token:
        raise HTTPException (
            status_code=status.HTTP_401_UNAUTHORIZED, detail=i18n.t ("_v1_user.auth.missing_token")
        )
    try:
        userId = await UserAuthService.validateToken (token)
        if not userId:
            raise HTTPException (
                status_code=status.HTTP_401_UNAUTHORIZED, detail=i18n.t ("_v1_user.auth.invalid_token")
            )
        return await UserAuthService.reverify (userId)
    except HTTPException:
        raise
    except Exception as e:
        logger = logging.getLogger (__name__)
        logger.error (f"Error in reverify endpoint: {e}", exc_info=True)
        raise HTTPException (
            status_code=status.HTTP_401_UNAUTHORIZED, detail=i18n.t ("_v1_user.auth.invalid_token")
        )

@userAuthPublicRouter.post (
    "/reset-password/{email}",
    status_code=Status.OK,
    dependencies=[Depends (RateLimiter (times=10, seconds=60)), Depends (urlGuard)],
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
                        "updated_at": "string",
                        "deleted_at": None
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
async def reset (
    email: str,
    signed: str = Query (..., description="The signed token"),
    dto: UserResetterUpdateValidatorDto = Body (
        None, examples={"default": {"value": {"password": "12345678", "password_confirmation": "12345678"}}}
    ),
) -> UserTransformerDto:
    """
    Reset Password
    """
    i18n = AppI18n.i18n ()
    if not dto:
        raise HTTPException (
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=i18n.t ("_v1_user.auth.request_body_required"),
        )
    return await UserAuthService.reset (signed, email, dto.password)

@userAuthRouter.post (
    "/forgot-password",
    status_code=Status.OK,
    dependencies=[Depends (RateLimiter (times=3, seconds=60))],
    response_model=str,
    responses={
        200: {
            "description": Description.OK,
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
                                    "email": "string"
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

async def forget (dto: UserIdentifierEmailDto = Body (..., examples={"email": "user@mail.com"})) -> str:
    """
    Forgot Password
    """
    return await UserAuthService.forget (dto.email)
