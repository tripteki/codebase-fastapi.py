from enum import Enum

class UserRoleEnum (str, Enum):
    """
    UserRoleEnum (str, Enum)

    Attributes:
        Superadmin (str)
        Admin (str)
        User (str)
    """
    Superadmin = "superadmin"
    Admin = "admin"
    User = "user"

    @classmethod
    def values (cls) -> tuple:
        """
        Returns:
            tuple
        """
        return tuple (role.value for role in cls)

    @classmethod
    def notify (cls) -> tuple:
        """
        Returns:
            tuple
        """
        return (cls.Superadmin, cls.Admin)

    @classmethod
    def activityReaders (cls) -> tuple:
        """
        Returns:
            tuple
        """
        return cls.notify ()

    @classmethod
    def systemSettings (cls) -> tuple:
        """
        Returns:
            tuple
        """
        return (cls.Superadmin,)

    @classmethod
    def privileged (cls) -> tuple:
        """
        Returns:
            tuple
        """
        return cls.notify ()
