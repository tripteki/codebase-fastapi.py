from enum import Enum

class UserAuthAccessTokenEnum (Enum):
    """
    UserAuthAccessTokenEnum (Enum)

    Attributes:
        METADATA (str)
    """
    METADATA = "accessToken"

class UserAuthRefreshTokenEnum (Enum):
    """
    UserAuthRefreshTokenEnum (Enum)

    Attributes:
        METADATA (str)
    """
    METADATA = "refreshToken"

class UserAuthAccessTokenMetadataMiddleware (Enum):
    """
    UserAuthAccessTokenMetadataMiddleware (Enum)

    Attributes:
        METADATA (str)
    """
    METADATA = "accessToken"

class UserAuthRefreshTokenMetadataMiddleware (Enum):
    """
    UserAuthRefreshTokenMetadataMiddleware (Enum)

    Attributes:
        METADATA (str)
    """
    METADATA = "refreshToken"
