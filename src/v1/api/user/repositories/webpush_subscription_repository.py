from datetime import datetime
from typing import List, Optional
from sqlmodel import Session, select
from src.app.bases.app_database import AppDatabase
from src.v1.api.user.databases.models.push_subscription_model import PushSubscription, USER_WEBPUSH_SUBSCRIBABLE_TYPE

class WebpushSubscriptionRepository:
    """
    WebpushSubscriptionRepository
    """
    @staticmethod
    def getSession () -> Session:
        """
        Returns:
            Session
        """
        engine = AppDatabase.databasePostgresql ()
        return Session (engine)

    @staticmethod
    async def updatePushSubscription (
        userId: str,
        endpoint: str,
        publicKey: Optional[str] = None,
        authToken: Optional[str] = None,
        contentEncoding: Optional[str] = None
    ) -> PushSubscription:
        """
        Args:
            userId (str)
            endpoint (str)
            publicKey (Optional[str])
            authToken (Optional[str])
            contentEncoding (Optional[str])
        Returns:
            PushSubscription
        """
        session = WebpushSubscriptionRepository.getSession ()
        try:
            statement = select (PushSubscription).where (PushSubscription.endpoint == endpoint)
            existing = session.exec (statement).first ()
            now = datetime.utcnow ()

            if (
                existing and
                existing.subscribable_id == userId and
                existing.subscribable_type == USER_WEBPUSH_SUBSCRIBABLE_TYPE
            ):
                existing.public_key = publicKey
                existing.auth_token = authToken
                existing.content_encoding = contentEncoding
                existing.updated_at = now
                session.add (existing)
                session.commit ()
                session.refresh (existing)
                return existing

            if existing:
                session.delete (existing)
                session.commit ()

            subscription = PushSubscription (
                subscribable_id=userId,
                subscribable_type=USER_WEBPUSH_SUBSCRIBABLE_TYPE,
                endpoint=endpoint,
                public_key=publicKey,
                auth_token=authToken,
                content_encoding=contentEncoding,
                created_at=now,
                updated_at=now,
            )
            session.add (subscription)
            session.commit ()
            session.refresh (subscription)
            return subscription
        finally:
            session.close ()

    @staticmethod
    async def deletePushSubscription (userId: str, endpoint: str) -> None:
        """
        Args:
            userId (str)
            endpoint (str)
        Returns:
            None
        """
        session = WebpushSubscriptionRepository.getSession ()
        try:
            statement = select (PushSubscription).where (
                PushSubscription.subscribable_id == userId,
                PushSubscription.subscribable_type == USER_WEBPUSH_SUBSCRIBABLE_TYPE,
                PushSubscription.endpoint == endpoint,
            )
            subscriptions = session.exec (statement).all ()
            for subscription in subscriptions:
                session.delete (subscription)
            session.commit ()
        finally:
            session.close ()

    @staticmethod
    async def hasPushSubscriptions (userId: str) -> bool:
        """
        Args:
            userId (str)
        Returns:
            bool
        """
        session = WebpushSubscriptionRepository.getSession ()
        try:
            statement = select (PushSubscription).where (
                PushSubscription.subscribable_id == userId,
                PushSubscription.subscribable_type == USER_WEBPUSH_SUBSCRIBABLE_TYPE,
            )
            return session.exec (statement).first () is not None
        finally:
            session.close ()

    @staticmethod
    async def findByUserId (userId: str) -> List[PushSubscription]:
        """
        Args:
            userId (str)
        Returns:
            List[PushSubscription]
        """
        session = WebpushSubscriptionRepository.getSession ()
        try:
            statement = select (PushSubscription).where (
                PushSubscription.subscribable_id == userId,
                PushSubscription.subscribable_type == USER_WEBPUSH_SUBSCRIBABLE_TYPE,
            )
            return list (session.exec (statement).all ())
        finally:
            session.close ()

    @staticmethod
    async def deleteById (subscriptionId: int) -> None:
        """
        Args:
            subscriptionId (int)
        Returns:
            None
        """
        session = WebpushSubscriptionRepository.getSession ()
        try:
            statement = select (PushSubscription).where (PushSubscription.id == subscriptionId)
            subscription = session.exec (statement).first ()
            if subscription:
                session.delete (subscription)
                session.commit ()
        finally:
            session.close ()
