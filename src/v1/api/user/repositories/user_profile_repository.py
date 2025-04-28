from datetime import datetime
from typing import List, Optional
from sqlmodel import Session, select
from ulid import ULID
from src.app.bases.app_auth import AppAuth
from src.app.bases.app_database import AppDatabase
from src.app.utils.app_avatar_storage import deleteAvatarIfExists
from src.v1.api.user.databases.models.profile_model import Profile
from src.v1.api.user.databases.models.user_model import User
from src.v1.api.user.repositories.user_auth_repository import UserAuthRepository

class UserProfileRepository:
    """
    UserProfileRepository
    """
    @staticmethod
    def getSession () -> Session:
        """
        Returns:
            Session
        """
        return Session (AppDatabase.databasePostgresql ())

    @staticmethod
    async def findProfileByUserId (userId: str) -> Optional[Profile]:
        """
        Args:
            userId (str)
        Returns:
            Optional[Profile]
        """
        session = UserProfileRepository.getSession ()
        try:
            return session.exec (
                select (Profile).where (Profile.user_id == userId)
            ).first ()
        finally:
            session.close ()

    @staticmethod
    async def getMe (userId: str) -> tuple[Optional[User], Optional[Profile]]:
        """
        Args:
            userId (str)
        Returns:
            tuple[Optional[User], Optional[Profile]]
        """
        user = await UserAuthRepository.findOneById (userId)
        if user is None:
            return None, None
        profile = await UserProfileRepository.findProfileByUserId (userId)
        return user, profile

    @staticmethod
    async def updateMe (
        userId: str,
        userData: dict,
        profileData: dict,
        avatarPath: Optional[str] = None,
    ) -> tuple[Optional[User], Optional[Profile]]:
        """
        Args:
            userId (str)
            userData (dict)
            profileData (dict)
            avatarPath (Optional[str])
        Returns:
            tuple[Optional[User], Optional[Profile]]
        """
        session = UserProfileRepository.getSession ()
        try:
            user = session.exec (
                select (User).where (User.id == userId, User.deleted_at == None)
            ).first ()
            if user is None:
                return None, None

            for key, value in userData.items ():
                setattr (user, key, value)
            user.updated_at = datetime.utcnow ()
            session.add (user)

            profile = session.exec (
                select (Profile).where (Profile.user_id == userId)
            ).first ()
            if profile is None:
                profile = Profile (
                    id=str (ULID ()),
                    user_id=userId,
                )

            if avatarPath is not None:
                deleteAvatarIfExists (profile.avatar)
                profileData["avatar"] = avatarPath

            for key, value in profileData.items ():
                setattr (profile, key, value)
            profile.updated_at = datetime.utcnow ()
            session.add (profile)
            session.commit ()
            session.refresh (user)
            session.refresh (profile)
            return user, profile
        except Exception:
            session.rollback ()
            raise
        finally:
            session.close ()

    @staticmethod
    async def profileInterests () -> List[str]:
        """
        Returns:
            List[str]
        """
        session = UserProfileRepository.getSession ()
        try:
            profiles = session.exec (
                select (Profile).where (Profile.interests != None)
            ).all ()
            values: set[str] = set ()
            for profile in profiles:
                for interest in profile.interests or []:
                    trimmed = str (interest).strip ()
                    if trimmed:
                        values.add (trimmed)
            return sorted (values)
        finally:
            session.close ()

    @staticmethod
    def hashPasswordIfPresent (userData: dict) -> dict:
        """
        Args:
            userData (dict)
        Returns:
            dict
        """
        password = userData.pop ("password", None)
        if password:
            userData["password"] = AppAuth.hashPassword (password)
        return userData
