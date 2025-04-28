import pytest
from httpx import AsyncClient
from sqlmodel import Session, select
from datetime import datetime

from src.app.bases.app_auth import AppAuth
from src.v1.api.user.databases.models.user_model import User
from test.helpers import update_user_verification, update_user_password, create_password_reset_token

class TestUserAuth:
    """User authentication tests"""

    @pytest.mark.asyncio
    async def test_auth_register_post (self, client: AsyncClient) -> None:
        """
        Test POST /api/v1/auth/register endpoint

        Should create a new user
        """
        import time

        response = await client.post (
            "/api/v1/auth/register",
            json={
                "name": f"test-user-{int (time.time ())}",
                "email": f"test-{int (time.time ())}@mail.com",
                "password": "12345678",
                "password_confirmation": "12345678"
            }
        )

        assert response.status_code == 201

        data = response.json ()
        assert "id" in data
        assert "email" in data
        assert "name" in data

    @pytest.mark.asyncio
    async def test_auth_login_post (self, client: AsyncClient, test_user: dict) -> None:
        """
        Test POST /api/v1/auth/login endpoint

        Should return access and refresh tokens
        """
        response = await client.post (
            "/api/v1/auth/login",
            json={
                "identifierKey": "email",
                "identifierValue": test_user["email"],
                "password": test_user["password"]
            }
        )

        assert response.status_code == 201

        data = response.json ()
        assert "accessToken" in data
        assert "refreshToken" in data
        assert "accessTokenTtl" in data
        assert "refreshTokenTtl" in data

    @pytest.mark.asyncio
    async def test_auth_logout_post (self, client: AsyncClient, test_user: dict) -> None:
        """
        Test POST /api/v1/auth/logout endpoint

        Should logout user and invalidate token
        """
        login_response = await client.post (
            "/api/v1/auth/login",
            json={
                "identifierKey": "email",
                "identifierValue": test_user["email"],
                "password": test_user["password"]
            }
        )

        assert login_response.status_code == 201
        login_data = login_response.json ()
        access_token = login_data["accessToken"]

        response = await client.post (
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == 200
        assert response.json () == True

    @pytest.mark.asyncio
    async def test_auth_refresh_put (self, client: AsyncClient, test_user: dict) -> None:
        """
        Test PUT /api/v1/auth/refresh endpoint

        Should return new access and refresh tokens
        """
        login_response = await client.post (
            "/api/v1/auth/login",
            json={
                "identifierKey": "email",
                "identifierValue": test_user["email"],
                "password": test_user["password"]
            }
        )

        assert login_response.status_code == 201
        refresh_token = login_response.json ()["refreshToken"]

        response = await client.put (
            "/api/v1/auth/refresh",
            headers={"Authorization": f"Bearer {refresh_token}"}
        )

        assert response.status_code == 200

        data = response.json ()
        assert "accessToken" in data
        assert "refreshToken" in data

    @pytest.mark.asyncio
    async def test_auth_me_get (self, client: AsyncClient, auth_token: str) -> None:
        """
        Test GET /api/v1/auth/me endpoint

        Should return authenticated user data
        """
        response = await client.get (
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 200

        data = response.json ()
        assert "id" in data
        assert "email" in data
        assert "name" in data

    @pytest.mark.asyncio
    async def test_auth_forgot_password_post (self, client: AsyncClient, test_user: dict) -> None:
        """
        Test POST /api/v1/auth/forgot-password endpoint

        Should send password reset email
        """
        response = await client.post (
            "/api/v1/auth/forgot-password",
            json={
                "email": test_user["email"]
            }
        )

        assert response.status_code == 200
        data = response.json ()
        assert isinstance (data, str)
        assert "reset link" in data.lower () or "email" in data.lower ()

    @pytest.mark.asyncio
    async def test_auth_reset_password_post (
        self,
        client: AsyncClient,
        test_user: dict,
        test_db: Session
    ) -> None:
        """
        Test POST /api/v1/auth/reset-password/{email} endpoint

        Should reset user password
        """
        from ulid import ULID
        from src.v1.api.user.databases.models.password_reset_token_model import PasswordResetToken

        token = str (str (ULID ()))
        create_password_reset_token (test_db, test_user["email"], token)

        response = await client.post (
            f"/api/v1/auth/reset-password/{test_user['email']}?signed={token}",
            json={
                "password": "newpassword123",
                "password_confirmation": "newpassword123"
            }
        )

        assert response.status_code == 200

        data = response.json ()
        assert "id" in data
        assert "email" in data

        hashed_password = AppAuth.hashPassword (test_user["password"])
        update_user_password (test_db, test_user["id"], hashed_password)

    @pytest.mark.asyncio
    async def test_auth_verify_email_post (
        self,
        client: AsyncClient,
        test_user: dict,
        auth_token: str,
        test_db: Session
    ) -> None:
        """
        Test POST /api/v1/auth/verify-email/{email} endpoint

        Should verify user email
        """
        from ulid import ULID
        from src.app.bases.app_context import AppContext

        stmt = select (User).where (User.id == test_user["id"])
        user = test_db.exec (stmt).first ()
        if user:
            user.email_verified_at = None
            test_db.add (user)
            test_db.commit ()

        token = str (ULID ())
        cache_redis = AppContext.cacheRedis ()
        await cache_redis.setex (f"verifier:{test_user['email']}", 3600, token)

        response = await client.post (
            f"/api/v1/auth/verify-email/{test_user['email']}?signed={token}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 200

        data = response.json ()
        assert "id" in data
        assert data["email_verified_at"] is not None

        update_user_verification (test_db, test_user["id"])

    @pytest.mark.asyncio
    async def test_auth_email_verification_notification_post (
        self,
        client: AsyncClient,
        auth_token: str
    ) -> None:
        """
        Test POST /api/v1/auth/email/verification-notification endpoint

        Should resend verification email
        """
        response = await client.post (
            "/api/v1/auth/email/verification-notification",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 200
        result = response.json ()
        assert isinstance (result, str)
        assert len (result) > 0

class TestUserAdmin:
    """User admin tests"""

    @pytest.mark.asyncio
    async def test_admin_users_index_get (self, client: AsyncClient, auth_token: str) -> None:
        """
        Test GET /api/v1/admin/users endpoint

        Should return list of users with pagination
        """
        response = await client.get (
            "/api/v1/admin/users/",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 200

        data = response.json ()
        assert "data" in data
        assert "totalPage" in data
        assert "currentPage" in data
        assert isinstance (data["data"], list)

    @pytest.mark.asyncio
    async def test_admin_users_show_get (
        self,
        client: AsyncClient,
        auth_token: str,
        test_user: dict
    ) -> None:
        """
        Test GET /api/v1/admin/users/{id} endpoint

        Should return specific user data
        """
        response = await client.get (
            f"/api/v1/admin/users/{test_user['id']}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 200

        data = response.json ()
        assert data["id"] == test_user["id"]
        assert "email" in data
        assert "name" in data

    @pytest.mark.asyncio
    async def test_admin_users_store_post (self, client: AsyncClient, auth_token: str) -> None:
        """
        Test POST /api/v1/admin/users endpoint

        Should create a new user
        """
        import time

        response = await client.post (
            "/api/v1/admin/users/",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "name": f"test-user-{int (time.time ())}",
                "email": f"test-{int (time.time ())}@mail.com",
                "password": "12345678",
                "password_confirmation": "12345678"
            }
        )

        assert response.status_code == 201

        data = response.json ()
        assert "id" in data
        assert "email" in data
        assert "name" in data

    @pytest.mark.asyncio
    async def test_admin_users_update_put (
        self,
        client: AsyncClient,
        auth_token: str,
        test_user: dict,
        test_db: Session
    ) -> None:
        """
        Test PUT /api/v1/admin/users/{id} endpoint

        Should update user data
        """
        import time

        response = await client.put (
            f"/api/v1/admin/users/{test_user['id']}",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "name": f"updated-user-{int (time.time ())}"
            }
        )

        assert response.status_code == 200

        data = response.json ()
        assert data["name"].startswith ("updated-user-")

        update_user_verification (test_db, test_user["id"])

    @pytest.mark.asyncio
    async def test_admin_users_verify_put (
        self,
        client: AsyncClient,
        auth_token: str,
        test_user: dict,
        test_db: Session
    ) -> None:
        """
        Test PUT /api/v1/admin/users/verify/{id} endpoint

        Should verify user email
        """
        update_user_verification (test_db, test_user["id"])

        response = await client.put (
            f"/api/v1/admin/users/verify/{test_user['id']}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 200

        data = response.json ()
        assert data["email_verified_at"] is not None

    @pytest.mark.asyncio
    async def test_admin_users_deactivate_delete (
        self,
        client: AsyncClient,
        auth_token: str,
        test_user: dict,
        test_db: Session
    ) -> None:
        """
        Test DELETE /api/v1/admin/users/deactivate/{id} endpoint

        Should deactivate (soft delete) user
        """
        update_user_verification (test_db, test_user["id"])

        response = await client.delete (
            f"/api/v1/admin/users/deactivate/{test_user['id']}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 200

        data = response.json ()
        assert data["deleted_at"] is not None

        update_user_verification (test_db, test_user["id"])

    @pytest.mark.asyncio
    async def test_admin_users_activate_delete (
        self,
        client: AsyncClient,
        auth_token: str,
        test_user: dict,
        test_db: Session
    ) -> None:
        """
        Test DELETE /api/v1/admin/users/activate/{id} endpoint

        Should activate (restore) user
        """
        deactivate_response = await client.delete (
            f"/api/v1/admin/users/deactivate/{test_user['id']}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert deactivate_response.status_code == 200

        response = await client.delete (
            f"/api/v1/admin/users/activate/{test_user['id']}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 200

        data = response.json ()
        assert data["deleted_at"] is None

        update_user_verification (test_db, test_user["id"])

    @pytest.mark.asyncio
    async def test_admin_users_import_post (
        self,
        client: AsyncClient,
        auth_token: str
    ) -> None:
        """
        Test POST /api/v1/admin/users/import endpoint

        Should import users from CSV file
        """
        import io

        csv_content = b"""name,email,password
Test User 1,import1@test.com,password123
Test User 2,import2@test.com,password123"""

        files = {
            "file": ("users.csv", io.BytesIO (csv_content), "text/csv")
        }

        response = await client.post (
            "/api/v1/admin/users/import",
            headers={"Authorization": f"Bearer {auth_token}"},
            files=files
        )

        assert response.status_code == 200
        result = response.json ()
        assert isinstance (result, str)
        assert len (result) > 0

    @pytest.mark.asyncio
    async def test_admin_users_export_post (
        self,
        client: AsyncClient,
        auth_token: str
    ) -> None:
        """
        Test POST /api/v1/admin/users/export endpoint

        Should export users to CSV file
        """
        response = await client.post (
            "/api/v1/admin/users/export",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "type": "csv"
            }
        )

        assert response.status_code == 200
        result = response.json ()
        assert isinstance (result, str)
        assert len (result) > 0
