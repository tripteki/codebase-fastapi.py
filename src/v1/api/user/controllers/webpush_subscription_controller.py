from fastapi import APIRouter, Depends, status, HTTPException
from src.app.dependencies.app_rate_limit import rateLimit
from src.app.dependencies.app_auth_api_dependency import get_current_user
from src.app.bases.app_security import security
from src.app.dtos.app_dto import Status, Description
from src.app.utils.app_response_helper import getStandardResponses
from src.v1.api.user.databases.models.user_model import User
from src.v1.api.user.dtos.webpush_validator_dto import (
    WebPushSubscribeValidatorDto,
    WebPushUnsubscribeValidatorDto,
    WebPushSuccessTransformerDto,
)
from src.v1.api.user.services.webpush_subscription_service import WebpushSubscriptionService

webpushSubscriptionRouter = APIRouter (prefix="/api/v1/webpush", tags=["WebPush"])

async def get_verified_user (current_user: User = Depends (get_current_user)) -> User:
    """
    Args:
        current_user (User)
    Returns:
        User
    """
    if current_user.email_verified_at is None:
        raise HTTPException (
            status_code=status.HTTP_403_FORBIDDEN,
            detail=Description.FORBIDDEN_UNVERIFIED,
        )
    return current_user

@webpushSubscriptionRouter.post (
    "/subscribe",
    status_code=Status.OK,
    dependencies=[rateLimit (times=10, seconds=60), Depends (security)],
    response_model=WebPushSuccessTransformerDto,
    responses=getStandardResponses (unauthorized=True, forbidden=True, unvalidated=True),
)
async def subscribe (
    dto: WebPushSubscribeValidatorDto,
    current_user: User = Depends (get_verified_user),
) -> WebPushSuccessTransformerDto:
    """
    Subscribe browser push subscription
    """
    return await WebpushSubscriptionService.subscribe (current_user.id, dto)

@webpushSubscriptionRouter.post (
    "/unsubscribe",
    status_code=Status.OK,
    dependencies=[rateLimit (times=10, seconds=60), Depends (security)],
    response_model=WebPushSuccessTransformerDto,
    responses=getStandardResponses (unauthorized=True, forbidden=True, unvalidated=True),
)
async def unsubscribe (
    dto: WebPushUnsubscribeValidatorDto,
    current_user: User = Depends (get_verified_user),
) -> WebPushSuccessTransformerDto:
    """
    Unsubscribe browser push subscription
    """
    return await WebpushSubscriptionService.unsubscribe (current_user.id, dto)
