from sqlmodel import Session, select
from datetime import datetime

def update_user_verification (test_db: Session, user_id: str) -> None:
    """
    Args:
        test_db (Session)
        user_id (str)
    Returns:
        None
    """
    from src.v1.api.user.databases.models.user_model import User

    stmt = select (User).where (User.id == user_id)
    user = test_db.exec (stmt).first ()
    if user:
        user.email_verified_at = datetime.utcnow ()
        user.deleted_at = None
        test_db.add (user)
        test_db.commit ()

def update_user_password (test_db: Session, user_id: str, hashed_password: str) -> None:
    """
    Args:
        test_db (Session)
        user_id (str)
        hashed_password (str)
    Returns:
        None
    """
    from src.v1.api.user.databases.models.user_model import User

    stmt = select (User).where (User.id == user_id)
    user = test_db.exec (stmt).first ()
    if user:
        user.password = hashed_password
        test_db.add (user)
        test_db.commit ()

def create_password_reset_token (test_db: Session, email: str, token: str) -> None:
    """
    Args:
        test_db (Session)
        email (str)
        token (str)
    Returns:
        None
    """
    from src.v1.api.user.databases.models.password_reset_token_model import PasswordResetToken

    reset_token = PasswordResetToken (
        email=email,
        token=token,
        created_at=datetime.utcnow ()
    )
    test_db.add (reset_token)
    test_db.commit ()

def create_notification (test_db: Session, notification_id: str, user_id: str, ntype: str, data: dict) -> None:
    """
    Args:
        test_db (Session)
        notification_id (str)
        user_id (str)
        ntype (str)
        data (dict)
    Returns:
        None
    """
    from src.v1.api.notification.databases.models.notification_model import Notification

    notification = Notification (
        id=notification_id,
        user_id=user_id,
        type=ntype,
        data=data,
        read_at=None,
        created_at=datetime.utcnow (),
        updated_at=datetime.utcnow ()
    )
    test_db.add (notification)
    test_db.commit ()
