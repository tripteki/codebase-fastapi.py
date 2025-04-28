from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict

class UserTransformerDto (BaseModel):
    """
    UserTransformerDto
    """
    id: str = Field (..., json_schema_extra={"example": "string"})
    name: str = Field (..., json_schema_extra={"example": "string"})
    email: EmailStr = Field (..., json_schema_extra={"example": "string"})
    email_verified_at: Optional[datetime] = Field (None, json_schema_extra={"example": None})
    created_at: datetime = Field (..., json_schema_extra={"example": "string"})
    updated_at: datetime = Field (..., json_schema_extra={"example": "string"})
    deleted_at: Optional[datetime] = Field (None, json_schema_extra={"example": None})

class UserAuthTransformerDto (BaseModel):
    """
    UserAuthTransformerDto
    """
    accessTokenTtl: int = Field (..., json_schema_extra={"example": 0})
    refreshTokenTtl: int = Field (..., json_schema_extra={"example": 0})
    accessToken: str = Field (..., json_schema_extra={"example": "string"})
    refreshToken: str = Field (..., json_schema_extra={"example": "string"})

class UserAuthIdentifierTransformerDto (BaseModel):
    """
    UserAuthIdentifierTransformerDto
    """
    userId: str = Field (..., json_schema_extra={"example": "string"})

class UserAuthIdentifierEmailTransformerDto (BaseModel):
    """
    UserAuthIdentifierEmailTransformerDto
    """
    userEmail: EmailStr = Field (..., json_schema_extra={"example": "string"})

class UserResetterTransformerDto (BaseModel):
    """
    UserResetterTransformerDto
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
