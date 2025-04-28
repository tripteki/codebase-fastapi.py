from enum import Enum

class UserAuthAccessTokenEnum (Enum):
    """
    UserAuthAccessTokenEnum
    """
    METADATA = "accessToken"

class UserAuthRefreshTokenEnum (Enum):
    """
    UserAuthRefreshTokenEnum
    """
    METADATA = "refreshToken"

class UserAuthAccessTokenMetadataMiddleware (Enum):
    """
    UserAuthAccessTokenMetadataMiddleware
    """
    METADATA = "accessToken"

class UserAuthRefreshTokenMetadataMiddleware (Enum):
    """
    UserAuthRefreshTokenMetadataMiddleware
    """
    METADATA = "refreshToken"
