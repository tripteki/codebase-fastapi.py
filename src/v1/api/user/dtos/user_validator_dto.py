from typing import Optional
from typing_extensions import Self
from pydantic import BaseModel, EmailStr, Field, model_validator

class UserIdentifierDto (BaseModel):
    """
    UserIdentifierDto (BaseModel)

    Attributes:
        id (str)
    """
    id: str = Field (..., json_schema_extra={"example": "01HZGXQZJQK9X5Y7Z8W9V0U1T2"})

class UserIdentifierEmailDto (BaseModel):
    """
    UserIdentifierEmailDto (BaseModel)

    Attributes:
        email (EmailStr)
    """
    email: EmailStr = Field (..., json_schema_extra={"example": "user@mail.com"})

class UserAuthDto (BaseModel):
    """
    UserAuthDto (BaseModel)

    Attributes:
        identifierKey (str)
        identifierValue (EmailStr)
        password (str)
    """
    identifierKey: str = Field (default="email", json_schema_extra={"example": "email"})
    identifierValue: EmailStr = Field (..., json_schema_extra={"example": "user@mail.com"})
    password: str = Field (..., min_length=8, json_schema_extra={"example": "12345678"})

class UserCreateValidatorDto (BaseModel):
    """
    UserCreateValidatorDto (BaseModel)

    Attributes:
        name (str)
        email (EmailStr)
        password (str)
        password_confirmation (str)
    """
    name: str = Field (..., min_length=1, max_length=255, json_schema_extra={"example": "user"})
    email: EmailStr = Field (..., json_schema_extra={"example": "user@mail.com"})
    password: str = Field (..., min_length=8, json_schema_extra={"example": "12345678"})
    password_confirmation: str = Field (..., min_length=8, json_schema_extra={"example": "12345678"})

    @model_validator (mode="after")
    def validate_password_confirmation (self) -> Self:
        """
        Args:
            self
        Returns:
            UserCreateValidatorDto
        """
        if self.password != self.password_confirmation:
            raise ValueError ("_v1_user.auth.password_mismatch")
        return self

class UserUpdateValidatorDto (BaseModel):
    """
    UserUpdateValidatorDto (BaseModel)

    Attributes:
        name (Optional[str])
        email (Optional[EmailStr])
        password (Optional[str])
        password_confirmation (Optional[str])
    """
    name: Optional[str] = Field (None, min_length=1, max_length=255, json_schema_extra={"example": "user"})
    email: Optional[EmailStr] = Field (None, json_schema_extra={"example": "user@mail.com"})
    password: Optional[str] = Field (None, min_length=8, json_schema_extra={"example": "12345678"})
    password_confirmation: Optional[str] = Field (None, min_length=8, json_schema_extra={"example": "12345678"})

    @model_validator (mode="after")
    def validate_password_confirmation (self) -> Self:
        """
        Args:
            self
        Returns:
            UserUpdateValidatorDto
        """
        if self.password is not None and self.password_confirmation is not None:
            if self.password != self.password_confirmation:
                raise ValueError ("_v1_user.auth.password_mismatch")
        elif self.password is not None and self.password_confirmation is None:
            raise ValueError ("_v1_user.auth.password_confirmation_required")
        elif self.password is None and self.password_confirmation is not None:
            raise ValueError ("_v1_user.auth.password_required")
        return self

class UserResetterUpdateValidatorDto (BaseModel):
    """
    UserResetterUpdateValidatorDto (BaseModel)

    Attributes:
        password (str)
        password_confirmation (str)
    """
    password: str = Field (..., min_length=8, json_schema_extra={"example": "12345678"})
    password_confirmation: str = Field (..., min_length=8, json_schema_extra={"example": "12345678"})

    @model_validator (mode="after")
    def validate_password_confirmation (self) -> Self:
        """
        Args:
            self
        Returns:
            UserResetterUpdateValidatorDto
        """
        if self.password != self.password_confirmation:
            raise ValueError ("_v1_user.auth.password_mismatch")
        return self

class UserExportTypeDto (BaseModel):
    """
    UserExportTypeDto (BaseModel)

    Attributes:
        type (Optional[str])
    """
    type: Optional[str] = Field (default="csv", pattern="^(csv|xls|xlsx)$", json_schema_extra={"example": "csv"})
