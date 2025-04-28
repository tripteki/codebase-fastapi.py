from datetime import datetime
from typing import Optional
from sqlmodel import Session, select
from src.app.bases.app_database import AppDatabase
from src.app.bases.app_auth import AppAuth
from src.v1.api.user.databases.models.user_model import User
from src.v1.api.user.databases.models.password_reset_token_model import PasswordResetToken

class UserAuthRepository:
    """
    UserAuthRepository
    """
    @staticmethod
    def getSession () -> Session:
        """
        Returns:
            Session
        """
        engine = AppDatabase.databasePostgresql ()
        return Session (engine)

    @staticmethod
    async def findOneByEmail (email: str) -> Optional[User]:
        """
        Args:
            email (str)
        Returns:
            Optional[User]
        """
        session = UserAuthRepository.getSession ()
        try:
            statement = select (User).where (User.email == email, User.deleted_at == None)
            result = session.exec (statement).first ()
            return result
        finally:
            session.close ()

    @staticmethod
    async def findOneById (id: str) -> Optional[User]:
        """
        Args:
            id (str)
        Returns:
            Optional[User]
        """
        session = UserAuthRepository.getSession ()
        try:
            statement = select (User).where (User.id == id, User.deleted_at == None)
            result = session.exec (statement).first ()
            return result
        finally:
            session.close ()

    @staticmethod
    async def findOneByIdIncludingDeleted (id: str) -> Optional[User]:
        """
        Args:
            id (str)
        Returns:
            Optional[User]
        """
        session = UserAuthRepository.getSession ()
        try:
            statement = select (User).where (User.id == id)
            result = session.exec (statement).first ()
            return result
        finally:
            session.close ()

    @staticmethod
    async def findOneDeletedById (id: str) -> Optional[User]:
        """
        Args:
            id (str)
        Returns:
            Optional[User]
        """
        session = UserAuthRepository.getSession ()
        try:
            statement = select (User).where (User.id == id, User.deleted_at != None)
            result = session.exec (statement).first ()
            return result
        finally:
            session.close ()

    @staticmethod
    async def create (user: User) -> User:
        """
        Args:
            user (User)
        Returns:
            User
        """
        session = UserAuthRepository.getSession ()
        try:
            session.add (user)
            session.commit ()
            session.refresh (user)
            return user
        finally:
            session.close ()

    @staticmethod
    async def update (user: User) -> User:
        """
        Args:
            user (User)
        Returns:
            User
        """
        session = UserAuthRepository.getSession ()
        try:
            session.add (user)
            session.commit ()
            session.refresh (user)
            return user
        finally:
            session.close ()

    @staticmethod
    async def logout (userId: str) -> Optional[User]:
        """
        Args:
            userId (str)
        Returns:
            Optional[User]
        """
        return await UserAuthRepository.findOneById (userId)

    @staticmethod
    async def me (userId: str) -> Optional[User]:
        """
        Args:
            userId (str)
        Returns:
            Optional[User]
        """
        return await UserAuthRepository.findOneById (userId)

    @staticmethod
    async def verify (userEmail: str) -> Optional[User]:
        """
        Args:
            userEmail (str)
        Returns:
            Optional[User]
        """
        session = UserAuthRepository.getSession ()
        try:
            statement = select (User).where (
                User.email == userEmail,
                User.deleted_at == None,
                User.email_verified_at == None
            )
            user = session.exec (statement).first ()
            if not user:
                return None
            user.email_verified_at = datetime.utcnow ()
            user.updated_at = datetime.utcnow ()
            session.add (user)
            session.commit ()
            session.refresh (user)
            return user
        finally:
            session.close ()

    @staticmethod
    async def reverify (userId: str) -> Optional[User]:
        """
        Args:
            userId (str)
        Returns:
            Optional[User]
        """
        return await UserAuthRepository.findOneById (userId)

    @staticmethod
    async def reset (token: str, email: str, password: str) -> Optional[User]:
        """
        Args:
            token (str)
            email (str)
            password (str)
        Returns:
            Optional[User]
        """
        session = UserAuthRepository.getSession ()
        try:
            statement = select (PasswordResetToken).where (
                PasswordResetToken.token == token,
                PasswordResetToken.email == email
            )
            resetToken = session.exec (statement).first ()
            if not resetToken:
                return None

            session.delete (resetToken)

            user = await UserAuthRepository.findOneByEmail (email)
            if not user:
                return None
            hashedPassword = AppAuth.hashPassword (password)
            user.password = hashedPassword
            user.updated_at = datetime.utcnow ()
            session.add (user)
            session.commit ()
            session.refresh (user)
            return user
        finally:
            session.close ()

    @staticmethod
    async def forget (token: str, email: str) -> Optional[PasswordResetToken]:
        """
        Args:
            token (str)
            email (str)
        Returns:
            Optional[PasswordResetToken]
        """
        session = UserAuthRepository.getSession ()
        try:
            user = await UserAuthRepository.findOneByEmail (email)
            if not user:
                return None

            statement = select (PasswordResetToken).where (PasswordResetToken.email == email)
            existingToken = session.exec (statement).first ()
            if existingToken:
                existingToken.token = token
                existingToken.created_at = datetime.utcnow ()
                session.add (existingToken)
                session.commit ()
                session.refresh (existingToken)
                return existingToken
            else:
                resetToken = PasswordResetToken (
                    token=token,
                    email=email,
                    created_at=datetime.utcnow ()
                )
                session.add (resetToken)
                session.commit ()
                session.refresh (resetToken)
                return resetToken
        finally:
            session.close ()
