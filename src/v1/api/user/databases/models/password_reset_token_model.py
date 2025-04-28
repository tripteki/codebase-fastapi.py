from datetime import datetime
from sqlmodel import SQLModel, Field

class PasswordResetToken (SQLModel, table=True):
    """
    PasswordResetToken (SQLModel)

    Attributes:
        token (str)
        email (str)
        created_at (datetime)
    """
    __tablename__ = "password_reset_tokens"
    token: str = Field (primary_key=True)
    email: str = Field (unique=True, index=True, foreign_key="users.email")
    created_at: datetime = Field (default_factory=datetime.utcnow)
