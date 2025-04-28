import pytest
from test.helpers import update_user_verification
from src.v1.api.user.databases.models.push_subscription_model import PushSubscription, USER_WEBPUSH_SUBSCRIBABLE_TYPE

class TestWebPush:
    """
    TestWebPush
    """
    @pytest.fixture (autouse=True)
    def setup (self, test_db, test_user):
        """
        Args:
            test_db
            test_user
        Returns:
            None
        """
        update_user_verification (test_db, test_user["id"])

    @pytest.mark.asyncio
    async def test_post_v1_webpush_subscribe (self, client, auth_token, test_db, test_user):
        """
        Test POST /api/v1/webpush/subscribe endpoint
        """
        response = await client.post (
            "/api/v1/webpush/subscribe",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "endpoint": "https://push.example.test/subscription",
                "keys": {
                    "p256dh": "test-p256dh",
                    "auth": "test-auth",
                },
            },
        )

        assert response.status_code == 200
        assert response.json ()["success"] is True

        from sqlmodel import select
        statement = select (PushSubscription).where (
            PushSubscription.subscribable_id == test_user["id"],
            PushSubscription.subscribable_type == USER_WEBPUSH_SUBSCRIBABLE_TYPE,
            PushSubscription.endpoint == "https://push.example.test/subscription",
        )
        subscription = test_db.exec (statement).first ()
        assert subscription is not None

    @pytest.mark.asyncio
    async def test_post_v1_webpush_unsubscribe (self, client, auth_token, test_db, test_user):
        """
        Test POST /api/v1/webpush/unsubscribe endpoint
        """
        await client.post (
            "/api/v1/webpush/subscribe",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "endpoint": "https://push.example.test/subscription",
                "keys": {
                    "p256dh": "test-p256dh",
                    "auth": "test-auth",
                },
            },
        )

        response = await client.post (
            "/api/v1/webpush/unsubscribe",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "endpoint": "https://push.example.test/subscription",
            },
        )

        assert response.status_code == 200
        assert response.json ()["success"] is True

        from sqlmodel import select
        statement = select (PushSubscription).where (
            PushSubscription.subscribable_id == test_user["id"],
            PushSubscription.endpoint == "https://push.example.test/subscription",
        )
        subscription = test_db.exec (statement).first ()
        assert subscription is None
