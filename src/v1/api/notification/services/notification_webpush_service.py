import asyncio
import json
import logging
from typing import Dict, List, Optional
from pywebpush import WebPushException, webpush
from src.app.configs.app_config import AppConfig
from src.app.configs.webpush_config import WebpushConfig
from src.v1.api.user.databases.models.push_subscription_model import PushSubscription
from src.v1.api.user.repositories.webpush_subscription_repository import WebpushSubscriptionRepository

logger = logging.getLogger (__name__)

class NotificationWebpushService:
    """
    NotificationWebpushService
    """
    @staticmethod
    def buildPayload (
        notificationId: str,
        notificationType: str,
        data: Dict[str, object],
        frontendUrl: str,
    ) -> Dict[str, object]:
        """
        Args:
            notificationId (str)
            notificationType (str)
            data (Dict[str, object])
            frontendUrl (str)
        Returns:
            Dict[str, object]
        """
        url = NotificationWebpushService.resolveUrl (data, frontendUrl)
        downloadUrl = NotificationWebpushService.resolveDownloadUrl (data)
        payloadData = {
            **data,
            "url": url,
            "notification_id": notificationId,
            "type": notificationType,
        }

        message: Dict[str, object] = {
            "title": NotificationWebpushService.resolveTitle (notificationType, data),
            "body": NotificationWebpushService.resolveBody (notificationType, data),
            "icon": "/manifest/icon-512x512.png",
            "badge": "/manifest/icon-192x192.png",
            "tag": f"notification_{notificationId}",
            "data": payloadData,
        }

        if downloadUrl:
            message["actions"] = [{"title": "Download", "action": downloadUrl}]
        elif url:
            message["actions"] = [{"title": "Open", "action": url}]

        return message

    @staticmethod
    def resolveTitle (notificationType: str, data: Dict[str, object]) -> str:
        """
        Args:
            notificationType (str)
            data (Dict[str, object])
        Returns:
            str
        """
        title = str (data.get ("title", "")).strip ()
        if title:
            return title

        message = str (data.get ("message", "")).strip ()
        if message:
            return message

        return notificationType

    @staticmethod
    def resolveBody (notificationType: str, data: Dict[str, object]) -> str:
        """
        Args:
            notificationType (str)
            data (Dict[str, object])
        Returns:
            str
        """
        lines: List[str] = []
        headline = str (data.get ("body_primary", "")).strip ()

        if headline:
            lines.append (headline)
        elif str (data.get ("filename", "")).strip ():
            lines.append (str (data.get ("filename", "")).strip ())
        else:
            message = str (data.get ("message", "")).strip ()
            title = str (data.get ("title", "")).strip ()
            if message and title and message != title:
                lines.append (message)

        secondary = str (data.get ("body_secondary", "")).strip ()
        if secondary:
            lines.append (secondary)
        elif str (data.get ("error", "")).strip ():
            lines.append (str (data.get ("error", "")).strip ())

        presentationLines = data.get ("presentation_lines")
        if isinstance (presentationLines, list):
            for line in presentationLines:
                if not isinstance (line, str) or not line.strip ():
                    continue
                lines.append (line.strip ())
                if len (lines) >= 4:
                    break

        if lines:
            return "\n".join (lines)

        totalImported = data.get ("totalImported")
        if totalImported is not None:
            imported = f"{int (totalImported):,}"
            skipped = f"{int (data.get ('totalSkipped', 0)):,}"
            return f"{imported} imported, {skipped} skipped"

        return NotificationWebpushService.resolveTitle (notificationType, data)

    @staticmethod
    def resolveUrl (data: Dict[str, object], frontendUrl: str) -> str:
        """
        Args:
            data (Dict[str, object])
            frontendUrl (str)
        Returns:
            str
        """
        for key in ("pdf_url", "fileUrl", "url"):
            value = data.get (key)
            if isinstance (value, str) and value.strip ():
                return value.strip ()

        return f"{frontendUrl.rstrip ('/')}/notifications"

    @staticmethod
    def resolveDownloadUrl (data: Dict[str, object]) -> Optional[str]:
        """
        Args:
            data (Dict[str, object])
        Returns:
            Optional[str]
        """
        fileUrl = data.get ("fileUrl")
        if isinstance (fileUrl, str) and fileUrl.strip ():
            return fileUrl.strip ()
        return None

    @staticmethod
    async def dispatch (
        userId: str,
        notificationId: str,
        notificationType: str,
        data: Dict[str, object],
    ) -> None:
        """
        Args:
            userId (str)
            notificationId (str)
            notificationType (str)
            data (Dict[str, object])
        Returns:
            None
        """
        config = WebpushConfig.config ()
        if not config.vapid_public_key.strip ():
            return

        subscriptions = await WebpushSubscriptionRepository.findByUserId (userId)
        if not subscriptions:
            return

        frontendUrl = AppConfig.config ().frontend_url
        payload = NotificationWebpushService.buildPayload (
            notificationId,
            notificationType,
            data,
            frontendUrl,
        )

        for subscription in subscriptions:
            await NotificationWebpushService.sendToSubscription (subscription, payload, config)

    @staticmethod
    async def dispatchAsync (
        userId: str,
        notificationId: str,
        notificationType: str,
        data: Dict[str, object],
    ) -> None:
        """
        Args:
            userId (str)
            notificationId (str)
            notificationType (str)
            data (Dict[str, object])
        Returns:
            None
        """
        asyncio.create_task (
            NotificationWebpushService.dispatch (userId, notificationId, notificationType, data)
        )

    @staticmethod
    async def sendToSubscription (
        subscription: PushSubscription,
        payload: Dict[str, object],
        config: WebpushConfig,
    ) -> None:
        """
        Args:
            subscription (PushSubscription)
            payload (Dict[str, object])
            config (WebpushConfig)
        Returns:
            None
        """
        try:
            await asyncio.to_thread (
                webpush,
                subscription_info={
                    "endpoint": subscription.endpoint,
                    "keys": {
                        "p256dh": subscription.public_key or "",
                        "auth": subscription.auth_token or "",
                    },
                },
                data=json.dumps (payload),
                vapid_private_key=config.vapid_private_key,
                vapid_claims={"sub": config.vapid_subject or AppConfig.config ().frontend_url},
            )
        except WebPushException as error:
            statusCode = getattr (error, "response", None)
            responseStatus = statusCode.status_code if statusCode is not None else None

            if responseStatus in (404, 410) and subscription.id is not None:
                await WebpushSubscriptionRepository.deleteById (subscription.id)
                return

            logger.warning (
                "Web push failed for subscription %s: %s",
                subscription.id,
                error,
            )
