from typing import Optional
from strawberry import input

@input
class UserAuthDto:
    """
    UserAuthDto
    """
    identifierKey: str
    identifierValue: str
    password: str
