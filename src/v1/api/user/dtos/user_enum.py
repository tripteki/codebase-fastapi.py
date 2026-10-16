from enum import Enum

class UserEnum (str, Enum):
    """
    UserEnum (str, Enum)

    Attributes:
        Superuser (str)
        Admin (str)
    """
    Superuser = "superuser"
    Admin = "admin"
