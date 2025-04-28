from datetime import datetime
from typing import Optional
from strawberry import type
from src.v1.api.user.databases.models.user_model import User

@type
class UserTransformerDto:
    """
    UserTransformerDto
    """
    id: str
    name: str
    email: str
    email_verified_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    @classmethod
    def fromModel (cls, user: User) -> "UserTransformerDto":
        """
        Args:
            user (User)
        Returns:
            UserTransformerDto
        """
        return cls (
            id=user.id,
            name=user.name,
            email=user.email,
            email_verified_at=user.email_verified_at,
            created_at=user.created_at,
            updated_at=user.updated_at,
            deleted_at=user.deleted_at
        )

@type
class UserAuthTransformerDto:
    """
    UserAuthTransformerDto
    """
    accessTokenTtl: Optional[float] = None
    refreshTokenTtl: Optional[float] = None
    accessToken: Optional[str] = None
    refreshToken: Optional[str] = None
