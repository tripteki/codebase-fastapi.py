import pytest
from httpx import AsyncClient
from sqlmodel import Session, select
from datetime import datetime

from src.v1.api.user.databases.models.user_model import User
from src.v1.api.notification.databases.models.notification_model import Notification
from test.helpers import update_user_verification, create_notification

@pytest.fixture (scope="function")
def test_notification (
    test_db: Session,
    test_user: dict
) -> str:
    """
    Create test notification

    Args:
        test_db: Test database session
        test_user: Test user data

    Returns:
        str: Notification ID
    """
    from ulid import ULID

    notification_id = str (ULID ())

    notification = Notification (
        id=notification_id,
        user_id=test_user["id"],
        type="test",
        data={"message": "Test notification"},
        read_at=None,
        created_at=datetime.utcnow (),
        updated_at=datetime.utcnow ()
    )
    test_db.add (notification)
    test_db.commit ()

    return notification_id

class TestNotification:
    """Notification user tests"""

    @pytest.fixture (autouse=True)
    def setup (self, test_db: Session, test_user: dict) -> None:
        """
        Ensure user is verified before each test
        """
        update_user_verification (test_db, test_user["id"])

    @pytest.mark.asyncio
    async def test_user_notifications_index_get (
        self,
        client: AsyncClient,
        auth_token: str
    ) -> None:
        """
        Test GET /api/v1/notifications endpoint

        Should return list of notifications with pagination
        """
        response = await client.get (
            "/api/v1/notifications/",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 200

        data = response.json ()
        assert "data" in data
        assert "totalPage" in data
        assert "currentPage" in data
        assert isinstance (data["data"], list)

    @pytest.mark.asyncio
    async def test_user_notifications_count_get (
        self,
        client: AsyncClient,
        auth_token: str
    ) -> None:
        """
        Test GET /api/v1/notifications/count endpoint

        Should return notification count
        """
        response = await client.get (
            "/api/v1/notifications/count",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 200

        data = response.json ()
        assert "count" in data
        assert isinstance (data["count"], int)

    @pytest.mark.asyncio
    async def test_user_notifications_read_all_put (
        self,
        client: AsyncClient,
        auth_token: str
    ) -> None:
        """
        Test PUT /api/v1/notifications/read-all endpoint

        Should mark all notifications as read
        """
        response = await client.put (
            "/api/v1/notifications/read-all",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 200

        data = response.json ()
        assert "count" in data
        assert isinstance (data["count"], int)

    @pytest.mark.asyncio
    async def test_user_notifications_read_put (
        self,
        client: AsyncClient,
        auth_token: str,
        test_notification: str
    ) -> None:
        """
        Test PUT /api/v1/notifications/read/{id} endpoint

        Should mark specific notification as read
        """
        response = await client.put (
            f"/api/v1/notifications/read/{test_notification}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 200

        data = response.json ()
        assert data["id"] == test_notification
        assert data["read_at"] is not None

    @pytest.mark.asyncio
    async def test_user_notifications_unread_get (
        self,
        client: AsyncClient,
        auth_token: str,
        test_user: dict,
        test_db: Session
    ) -> None:
        """
        Test GET /api/v1/notifications/unread endpoint

        Should return unread notification count
        """
        update_user_verification (test_db, test_user["id"])

        response = await client.get (
            "/api/v1/notifications/unread",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 200

        data = response.json ()
        assert "unread" in data
        assert isinstance (data["unread"], int)

    @pytest.mark.asyncio
    async def test_user_notifications_show_get (
        self,
        client: AsyncClient,
        auth_token: str,
        test_user: dict,
        test_notification: str,
        test_db: Session
    ) -> None:
        """
        Test GET /api/v1/notifications/{id} endpoint

        Should return specific notification data
        """
        update_user_verification (test_db, test_user["id"])

        response = await client.get (
            f"/api/v1/notifications/{test_notification}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 200

        data = response.json ()
        assert data["id"] == test_notification
        assert "type" in data
        assert "data" in data

    @pytest.mark.asyncio
    async def test_user_notifications_destroy_delete (
        self,
        client: AsyncClient,
        auth_token: str,
        test_user: dict,
        test_notification: str,
        test_db: Session
    ) -> None:
        """
        Test DELETE /api/v1/notifications/{id} endpoint

        Should delete notification
        """
        update_user_verification (test_db, test_user["id"])

        response = await client.delete (
            f"/api/v1/notifications/{test_notification}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 200

        from ulid import ULID
        new_notification_id = str (ULID ())

        create_notification (test_db, new_notification_id, test_user["id"], "test", {"message": "Test notification for admin"})

        return new_notification_id

class TestNotificationAdmin:
    """Notification admin tests"""

    @pytest.fixture (autouse=True)
    def setup (self, test_db: Session, test_user: dict) -> None:
        """
        Ensure user is verified before each test
        """
        update_user_verification (test_db, test_user["id"])

    @pytest.mark.asyncio
    async def test_admin_notifications_index_get (
        self,
        client: AsyncClient,
        auth_token: str
    ) -> None:
        """
        Test GET /api/v1/admin/notifications endpoint

        Should return list of all notifications with pagination
        """
        response = await client.get (
            "/api/v1/admin/notifications/",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 200

        data = response.json ()
        assert "data" in data
        assert "totalPage" in data
        assert isinstance (data["data"], list)

    @pytest.mark.asyncio
    async def test_admin_notifications_show_get (
        self,
        client: AsyncClient,
        auth_token: str,
        test_notification: str
    ) -> None:
        """
        Test GET /api/v1/admin/notifications/{id} endpoint

        Should return specific notification data
        """
        response = await client.get (
            f"/api/v1/admin/notifications/{test_notification}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 200

        data = response.json ()
        assert data["id"] == test_notification
        assert "type" in data
        assert "data" in data

    @pytest.mark.asyncio
    async def test_admin_notifications_deactivate_delete (
        self,
        client: AsyncClient,
        auth_token: str,
        test_notification: str
    ) -> None:
        """
        Test DELETE /api/v1/admin/notifications/deactivate/{id} endpoint

        Should deactivate (soft delete) notification
        """
        response = await client.delete (
            f"/api/v1/admin/notifications/deactivate/{test_notification}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 200

        data = response.json ()
        assert data["deleted_at"] is not None

    @pytest.mark.asyncio
    async def test_admin_notifications_activate_delete (
        self,
        client: AsyncClient,
        auth_token: str,
        test_notification: str
    ) -> None:
        """
        Test DELETE /api/v1/admin/notifications/activate/{id} endpoint

        Should activate (restore) notification
        """
        response = await client.delete (
            f"/api/v1/admin/notifications/activate/{test_notification}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 200

        data = response.json ()
        assert data["deleted_at"] is None
