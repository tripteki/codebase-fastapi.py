from typing import Optional
from fastapi import APIRouter, Body, Depends, HTTPException, Query, Request, Response, status
from fastapi.security import HTTPAuthorizationCredentials
from fastapi_limiter.depends import RateLimiter
from src.app.bases.app_i18n import AppI18n
from src.app.bases.app_security import security
from src.app.dependencies.app_url_guard import urlGuard
from src.app.dependencies.app_auth_api_dependency import get_current_user
from src.app.dtos.app_dto import Status, Description
from src.app.utils.app_response_helper import getStandardResponses
from src.v1.api.user.databases.models.user_model import User
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
    responses=getStandardResponses (bad_request=True, unvalidated=True)
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
    responses=getStandardResponses (unauthorized=True, forbidden=True)
)
async def logout (
    request: Request,
    current_user: User = Depends (get_current_user)
) -> bool:
    """
    Logout
    """
    token = UserAuthService.httpBearerToken (request)
    if not token:
        return False
    result = await UserAuthService.logout (current_user.id, token)
    return bool (result)

@userAuthRouter.put (
    "/refresh",
    status_code=Status.OK,
    dependencies=[Depends (RateLimiter (times=3, seconds=60)), Depends (security)],
    response_model=UserAuthTransformerDto,
    responses=getStandardResponses (unauthorized=True, forbidden=True)
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
    responses=getStandardResponses (unauthorized=True, forbidden=True)
)
async def me (
    current_user: User = Depends (get_current_user)
) -> UserTransformerDto:
    """
    Get Current User
    """
    return await UserAuthService.me (current_user.id)

@userAuthRouter.post (
    "/register",
    status_code=Status.CREATED,
    dependencies=[Depends (RateLimiter (times=5, seconds=60))],
    response_model=UserTransformerDto,
    responses=getStandardResponses (bad_request=True, unvalidated=True)
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
    responses=getStandardResponses (forbidden=True, not_found=True)
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
    responses=getStandardResponses (unauthorized=True, forbidden=True)
)
async def reverify (
    current_user: User = Depends (get_current_user)
) -> str:
    """
    Resend Email Verification
    """
    return await UserAuthService.reverify (current_user.id)

@userAuthPublicRouter.post (
    "/reset-password/{email}",
    status_code=Status.OK,
    dependencies=[Depends (RateLimiter (times=10, seconds=60)), Depends (urlGuard)],
    response_model=UserTransformerDto,
    responses=getStandardResponses (forbidden=True, not_found=True, unvalidated=True)
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
    responses=getStandardResponses (bad_request=True, unvalidated=True)
)

async def forget (dto: UserIdentifierEmailDto = Body (..., examples={"email": "user@mail.com"})) -> str:
    """
    Forgot Password
    """
    return await UserAuthService.forget (dto.email)
