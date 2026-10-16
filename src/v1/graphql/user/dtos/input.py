from typing import Optional
from strawberry import input

@input
class UserAuthDto:
    """
    UserAuthDto

    Attributes:
        identifierKey (str)
        identifierValue (str)
        password (str)
        remember (Optional[bool])
    """
    identifierKey: str
    identifierValue: str
    password: str
    remember: Optional[bool] = None
