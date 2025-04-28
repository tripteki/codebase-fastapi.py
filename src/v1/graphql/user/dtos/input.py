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
    """
    identifierKey: str
    identifierValue: str
    password: str
