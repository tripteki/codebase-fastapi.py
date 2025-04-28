import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator, Dict, Generator
from httpx import AsyncClient, ASGITransport
from sqlmodel import Session, create_engine, select
from datetime import datetime

from src.app.configs.app_config import AppConfig
from src.app.configs.database_config import DatabaseConfig
from src.app.bases.app_database import AppDatabase
from src.app.bases.app_auth import AppAuth
from src.v1.api.user.databases.models.user_model import User
from src.v1.api.user.databases.models.password_reset_token_model import PasswordResetToken
from src.v1.api.notification.databases.models.notification_model import Notification

@pytest.fixture (scope="session")
def anyio_backend () -> str:
    """
    Args:
    Returns:
        str
    """
    return "asyncio"

@pytest.fixture (scope="function")
def test_db () -> Generator[Session, None, None]:
    """
    Args:
    Returns:
        Generator[Session, None, None]
    """
    engine = AppDatabase.databasePostgresql ()

    with Session (engine) as session:
        yield session

@pytest_asyncio.fixture (scope="function")
async def client (test_db: Session) -> AsyncGenerator[AsyncClient, None]:
    """
    Args:
        test_db (Session)
    Returns:
        AsyncGenerator[AsyncClient, None]
    """
    from main import app, lifespan
    from unittest.mock import AsyncMock, patch

    with patch ('fastapi_limiter.FastAPILimiter.redis', new=AsyncMock ()):
        with patch ('fastapi_limiter.FastAPILimiter.identifier', new=AsyncMock ()):
            with patch ('fastapi_limiter.FastAPILimiter.http_callback', new=AsyncMock ()):
                async with lifespan (app):
                    async with AsyncClient (transport=ASGITransport (app=app), base_url="http://test") as ac:
                        yield ac

@pytest.fixture (scope="function")
def test_user (test_db: Session) -> Dict:
    """
    Args:
        test_db (Session)
    Returns:
        Dict
    """
    from ulid import ULID

    test_email = "user@mail.com"
    test_password = "12345678"

    hashed_password = AppAuth.hashPassword (test_password)

    statement = select (User).where (User.email == test_email)
    existing_user = test_db.exec (statement).first ()

    if existing_user:
        existing_user.password = hashed_password
        existing_user.email_verified_at = datetime.utcnow ()
        existing_user.deleted_at = None
        existing_user.updated_at = datetime.utcnow ()
        test_db.add (existing_user)
        test_db.commit ()
        test_db.refresh (existing_user)
        user_id = existing_user.id
    else:
        user_id = str (ULID ())
        new_user = User (
            id=user_id,
            name=f"test-user-{str (ULID ())}",
            email=test_email,
            password=hashed_password,
            email_verified_at=datetime.utcnow (),
            created_at=datetime.utcnow (),
            updated_at=datetime.utcnow ()
        )
        test_db.add (new_user)
        test_db.commit ()
        test_db.refresh (new_user)

    return {
        "id": user_id,
        "email": test_email,
        "password": test_password,
    }

@pytest.fixture (scope="function")
def auth_token (test_user: Dict) -> str:
    """
    Args:
        test_user (Dict)
    Returns:
        str
    """
    return AppAuth.createAccessToken ({"sub": test_user["id"]})

@pytest.fixture (scope="function", autouse=True)
def cleanup_test_data (test_db: Session, test_user: Dict) -> None:
    """
    Args:
        test_db (Session)
        test_user (Dict)
    Returns:
        None
    """
    try:
        stmt = select (PasswordResetToken).where (PasswordResetToken.email == test_user["email"])
        tokens = test_db.exec (stmt).all ()
        for token in tokens:
            test_db.delete (token)
        test_db.commit ()
    except Exception as e:
        test_db.rollback ()
        print (f"Pre-cleanup error: {e}")

    yield

    try:
        stmt = select (PasswordResetToken).where (PasswordResetToken.email == test_user["email"])
        tokens = test_db.exec (stmt).all ()
        for token in tokens:
            test_db.delete (token)

        stmt = select (Notification).where (Notification.user_id == test_user["id"])
        notifications = test_db.exec (stmt).all ()
        for notification in notifications:
            test_db.delete (notification)

        test_db.commit ()
    except Exception as e:
        test_db.rollback ()
        print (f"Cleanup error: {e}")
