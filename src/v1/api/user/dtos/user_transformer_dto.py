from datetime import datetime
from typing import Optional, List
from typing_extensions import Self
from pydantic import BaseModel, EmailStr, Field
from src.v1.api.user.databases.models.user_model import User
from src.v1.api.user.databases.models.profile_model import Profile

class UserProfileTransformerDto (BaseModel):
    """
    UserProfileTransformerDto (BaseModel)
    """
    full_name: Optional[str] = Field (None, json_schema_extra={"example": "string"})
    avatar: Optional[str] = Field (None, json_schema_extra={"example": None})
    avatar_url: Optional[str] = Field (None, json_schema_extra={"example": None})
    interests: Optional[List[str]] = Field (default_factory=list, json_schema_extra={"example": []})

    @staticmethod
    def fromProfile (profile: Optional[Profile], appUrl: str = "") -> Optional["UserProfileTransformerDto"]:
        """
        Args:
            profile (Optional[Profile])
            appUrl (str)
        Returns:
            Optional[UserProfileTransformerDto]
        """
        if profile is None:
            return None

        avatarUrl = None
        if profile.avatar:
            avatarUrl = f"{appUrl.rstrip ('/')}/storage/{profile.avatar.lstrip ('/')}"

        return UserProfileTransformerDto (
            full_name=profile.full_name,
            avatar=profile.avatar,
            avatar_url=avatarUrl,
            interests=profile.interests or [],
        )

class UserMeTransformerDto (BaseModel):
    """
    UserMeTransformerDto (BaseModel)
    """
    id: str = Field (..., json_schema_extra={"example": "string"})
    name: str = Field (..., json_schema_extra={"example": "string"})
    email: EmailStr = Field (..., json_schema_extra={"example": "string"})
    email_verified_at: Optional[datetime] = Field (None, json_schema_extra={"example": None})
    created_at: datetime = Field (..., json_schema_extra={"example": "string"})
    updated_at: datetime = Field (..., json_schema_extra={"example": "string"})
    profile: Optional[UserProfileTransformerDto] = Field (None, json_schema_extra={"example": None})

    @staticmethod
    def fromUser (user: User, profile: Optional[Profile] = None, appUrl: str = "") -> Self:
        """
        Args:
            user (User)
            profile (Optional[Profile])
            appUrl (str)
        Returns:
            UserMeTransformerDto
        """
        return UserMeTransformerDto (
            id=user.id,
            name=user.name,
            email=user.email,
            email_verified_at=user.email_verified_at,
            created_at=user.created_at,
            updated_at=user.updated_at,
            profile=UserProfileTransformerDto.fromProfile (profile, appUrl),
        )

class UserAccessTransformerDto (BaseModel):
    """
    UserAccessTransformerDto (BaseModel)
    """
    permissions: List[str] = Field (default_factory=list, json_schema_extra={"example": []})
    roles: List[str] = Field (default_factory=list, json_schema_extra={"example": []})

class UserTransformerDto (BaseModel):
    """
    UserTransformerDto (BaseModel)

    Attributes:
        id (str)
        name (str)
        email (EmailStr)
        email_verified_at (Optional[datetime])
        created_at (datetime)
        updated_at (datetime)
        deleted_at (Optional[datetime])
    """
    id: str = Field (..., json_schema_extra={"example": "string"})
    name: str = Field (..., json_schema_extra={"example": "string"})
    email: EmailStr = Field (..., json_schema_extra={"example": "string"})
    email_verified_at: Optional[datetime] = Field (None, json_schema_extra={"example": None})
    created_at: datetime = Field (..., json_schema_extra={"example": "string"})
    updated_at: datetime = Field (..., json_schema_extra={"example": "string"})
    deleted_at: Optional[datetime] = Field (None, json_schema_extra={"example": None})

    @staticmethod
    def fromUser (user: User) -> Self:
        """
        Args:
            user (User)
        Returns:
            UserTransformerDto
        """
        return UserTransformerDto (
            id=user.id,
            name=user.name,
            email=user.email,
            email_verified_at=user.email_verified_at,
            created_at=user.created_at,
            updated_at=user.updated_at,
            deleted_at=user.deleted_at
        )

class UserAuthTransformerDto (BaseModel):
    """
    UserAuthTransformerDto (BaseModel)

    Attributes:
        accessTokenTtl (int)
        refreshTokenTtl (int)
        accessToken (str)
        refreshToken (str)
    """
    accessTokenTtl: int = Field (..., json_schema_extra={"example": 0})
    refreshTokenTtl: int = Field (..., json_schema_extra={"example": 0})
    accessToken: str = Field (..., json_schema_extra={"example": "string"})
    refreshToken: str = Field (..., json_schema_extra={"example": "string"})

class UserAuthIdentifierTransformerDto (BaseModel):
    """
    UserAuthIdentifierTransformerDto (BaseModel)

    Attributes:
        userId (str)
    """
    userId: str = Field (..., json_schema_extra={"example": "string"})

class UserAuthIdentifierEmailTransformerDto (BaseModel):
    """
    UserAuthIdentifierEmailTransformerDto (BaseModel)

    Attributes:
        userEmail (EmailStr)
    """
    userEmail: EmailStr = Field (..., json_schema_extra={"example": "string"})

class UserResetterTransformerDto (BaseModel):
    """
    UserResetterTransformerDto (BaseModel)

    Attributes:
        token (str)
        email (EmailStr)
        created_at (datetime)
        user (UserTransformerDto)
    """
    token: str = Field (..., json_schema_extra={"example": "string"})
    email: EmailStr = Field (..., json_schema_extra={"example": "string"})
    created_at: datetime = Field (..., json_schema_extra={"example": "string"})
    user: UserTransformerDto = Field (..., json_schema_extra={"example": {
        "id": "string",
        "name": "string",
        "email": "string",
        "email_verified_at": None,
        "created_at": "string",
        "updated_at": "string",
        "deleted_at": None
    }})
