from src.v1.api.user.dtos.webpush_validator_dto import (
    WebPushSubscribeValidatorDto,
    WebPushUnsubscribeValidatorDto,
    WebPushSuccessTransformerDto,
)
from src.v1.api.user.repositories.webpush_subscription_repository import WebpushSubscriptionRepository

class WebpushSubscriptionService:
    """
    WebpushSubscriptionService
    """
    @staticmethod
    async def subscribe (userId: str, data: WebPushSubscribeValidatorDto) -> WebPushSuccessTransformerDto:
        """
        Args:
            userId (str)
            data (WebPushSubscribeValidatorDto)
        Returns:
            WebPushSuccessTransformerDto
        """
        await WebpushSubscriptionRepository.updatePushSubscription (
            userId,
            data.endpoint,
            data.keys.p256dh if data.keys else None,
            data.keys.auth if data.keys else None,
            data.content_encoding,
        )
        return WebPushSuccessTransformerDto (success=True)

    @staticmethod
    async def unsubscribe (userId: str, data: WebPushUnsubscribeValidatorDto) -> WebPushSuccessTransformerDto:
        """
        Args:
            userId (str)
            data (WebPushUnsubscribeValidatorDto)
        Returns:
            WebPushSuccessTransformerDto
        """
        await WebpushSubscriptionRepository.deletePushSubscription (userId, data.endpoint)
        return WebPushSuccessTransformerDto (success=True)
