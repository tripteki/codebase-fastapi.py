from datetime import datetime
from typing import Any, Optional, List, Dict
from sqlalchemy import case, func, or_
from sqlmodel import Session, col, select
from ulid import ULID
from src.app.bases.app_auth import AppAuth
from src.app.configs.app_config import AppConfig
from src.app.bases.app_database import AppDatabase
from src.app.repositories.app_postgresql_repository import AppPostgresqlRepository
from src.app.repositories.app_repository import OffsetPagination, OffsetPaginationType, CursorPagination, CursorPaginationType, Orderization, Filterization
from src.v1.api.notification.databases.models.notification_model import Notification
from src.v1.api.user.databases.models.acl_model import ModelHasRole, Role
from src.v1.api.user.databases.models.password_reset_token_model import PasswordResetToken
from src.v1.api.user.databases.models.profile_model import Profile
from src.v1.api.user.databases.models.push_subscription_model import PushSubscription
from src.v1.api.user.databases.models.user_model import User
from src.v1.api.user.repositories.user_acl_repository import GUARD_NAME, USER_MODEL_TYPE, UserAclRepository
from src.v1.api.user.dtos.user_transformer_dto import UserTransformerDto

SORTABLE_FIELDS = ("email", "created_at", "updated_at")

class UserAdminRepository (AppPostgresqlRepository[User]):
    """
    UserAdminRepository (AppPostgresqlRepository)
    """
    def __init__ (self) -> None:
        """
        Returns:
        """
        super ().__init__ ()

    @staticmethod
    def getSession () -> Session:
        """
        Returns:
            Session
        """
        engine = AppDatabase.databasePostgresql ()
        return Session (engine)

    @staticmethod
    def _normalizeFilters (filters: Optional[List[Any]]) -> Dict[str, str]:
        """
        Args:
            filters (Optional[List[Any]])
        Returns:
            Dict[str, str]
        """
        normalized: Dict[str, str] = {}
        for item in filters or []:
            if isinstance (item, dict):
                field = str (item.get ("field") or "").strip ()
                search = str (item.get ("search") or "").strip ()
            else:
                field = str (getattr (item, "field", "") or "").strip ()
                search = str (getattr (item, "search", "") or "").strip ()
            if field and search:
                normalized[field] = search
        return normalized

    @staticmethod
    def _normalizeOrders (orders: Optional[List[Any]]) -> List[tuple]:
        """
        Args:
            orders (Optional[List[Any]])
        Returns:
            List[tuple]
        """
        normalized: List[tuple] = []
        for item in orders or []:
            if isinstance (item, dict):
                field = str (item.get ("field") or "").strip ()
                direction = str (item.get ("direction") or "asc").strip ().lower ()
            else:
                field = str (getattr (item, "field", "") or "").strip ()
                direction = str (getattr (item, "direction", "asc") or "asc").strip ().lower ()
            if field:
                normalized.append ((field, "desc" if direction == "desc" else "asc"))
        return normalized or [("created_at", "desc")]

    @classmethod
    def _conditions (cls, filters: Optional[List[Any]]) -> List[Any]:
        """
        Args:
            filters (Optional[List[Any]])
        Returns:
            List[Any]
        """
        filterMap = cls._normalizeFilters (filters)
        conditions: List[Any] = []
        status = filterMap.get ("status", "active")
        conditions.extend ({
            "active": (User.deleted_at == None, User.email_verified_at != None),
            "unverified": (User.deleted_at == None, User.email_verified_at == None),
            "deactivated": (User.deleted_at != None,),
        }.get (status, ()))
        q = filterMap.get ("q") or filterMap.get ("search")
        if q:
            pattern = f"%{q}%"
            profileIds = select (Profile.user_id).where (col (Profile.full_name).ilike (pattern))
            conditions.append (or_ (
                col (User.email).ilike (pattern),
                col (User.name).ilike (pattern),
                col (User.id).in_ (profileIds),
            ))
        roleName = filterMap.get ("role")
        if roleName:
            roleSubquery = (
                select (ModelHasRole.model_id)
                .join (Role, Role.id == ModelHasRole.role_id)
                .where (
                    ModelHasRole.model_type == USER_MODEL_TYPE,
                    Role.name == roleName,
                    Role.guard_name == GUARD_NAME,
                )
            )
            conditions.append (User.id.in_ (roleSubquery))
        return conditions

    @classmethod
    def _orderBy (cls, orders: Optional[List[Any]]) -> List[Any]:
        """
        Args:
            orders (Optional[List[Any]])
        Returns:
            List[Any]
        """
        columns: List[Any] = []
        for field, direction in cls._normalizeOrders (orders):
            if field == "status":
                column = case (
                    (User.deleted_at != None, 2),
                    (User.email_verified_at == None, 1),
                    else_=0,
                )
            elif field in SORTABLE_FIELDS:
                column = getattr (User, field)
            else:
                continue
            columns.append (column.desc () if direction == "desc" else column.asc ())
        return columns

    async def allFiltered (
        self,
        orders: List[Orderization] = None,
        filters: List[Filterization] = None,
    ) -> List[User]:
        """
        Args:
            orders (List[Orderization])
            filters (List[Filterization])
        Returns:
            List[User]
        """
        session = self.getSession ()
        try:
            return list (session.exec (
                select (User).where (*self._conditions (filters)).order_by (*self._orderBy (orders))
            ).all ())
        finally:
            session.close ()

    async def allOffset (
        self,
        userId: str,
        orders: List[Orderization] = None,
        filters: List[Filterization] = None,
        page: OffsetPaginationType = None
    ) -> OffsetPagination[UserTransformerDto]:
        """
        Args:
            userId (str)
            orders (List[Orderization])
            filters (List[Filterization])
            page (OffsetPaginationType)
        Returns:
            OffsetPagination[UserTransformerDto]
        """
        page = page or OffsetPaginationType (currentPage=1, limitPage=10)
        conditions = self._conditions (filters)

        session = self.getSession ()
        try:
            statement = select (User).where (*conditions).order_by (*self._orderBy (orders))
            countStatement = select (func.count ()).select_from (User).where (*conditions)
            total = int (session.exec (countStatement).one ())
            offset = (page.currentPage - 1) * page.limitPage
            users = session.exec (statement.offset (offset).limit (page.limitPage)).all ()
            userIds = [user.id for user in users]
            profiles = {}
            if userIds:
                for profile in session.exec (
                    select (Profile).where (col (Profile.user_id).in_ (userIds))
                ).all ():
                    profiles[profile.user_id] = profile
            appUrl = (AppConfig.config ().frontend_url or "").rstrip ("/")
            data = []
            for user in users:
                role = await UserAclRepository.getUserRole (user.id)
                data.append (UserTransformerDto.fromUser (user, role, profiles.get (user.id), appUrl))
            perPage = page.limitPage
            currentPage = page.currentPage
            lastPage = (total + perPage - 1) // perPage if total > 0 else 1
            return OffsetPagination (
                total=int (total),
                totalPage=lastPage,
                perPage=perPage,
                currentPage=currentPage,
                nextPage=currentPage + 1 if currentPage < lastPage else None,
                previousPage=currentPage - 1 if currentPage > 1 else None,
                firstPage=1,
                lastPage=lastPage,
                data=data
            )
        finally:
            session.close ()

    async def upsertProfile (
        self,
        userId: str,
        fullName: Optional[str] = None,
        avatarPath: Optional[str] = None,
    ) -> None:
        """
        Args:
            userId (str)
            fullName (Optional[str])
            avatarPath (Optional[str])
        Returns:
            None
        """
        from src.app.utils.app_avatar_storage import deleteAvatarIfExists

        session = self.getSession ()
        try:
            profile = session.exec (
                select (Profile).where (Profile.user_id == userId)
            ).first ()
            if profile is None:
                session.add (Profile (
                    user_id=userId,
                    full_name=fullName,
                    avatar=avatarPath,
                ))
            else:
                if fullName is not None:
                    profile.full_name = fullName
                if avatarPath is not None:
                    deleteAvatarIfExists (profile.avatar)
                    profile.avatar = avatarPath
                profile.updated_at = datetime.utcnow ()
                session.add (profile)
            session.commit ()
        except Exception:
            session.rollback ()
            raise
        finally:
            session.close ()

    async def allCursor (
        self,
        userId: str,
        orders: List[Orderization] = None,
        filters: List[Filterization] = None,
        page: CursorPaginationType = None
    ) -> CursorPagination[User]:
        """
        Args:
            userId (str)
            orders (List[Orderization])
            filters (List[Filterization])
            page (CursorPaginationType)
        Returns:
            CursorPagination[User]
        """
        orders = orders or []
        filters = filters or []
        page = page or CursorPaginationType (cursorField="id", cursorPage=None, limitPage=10)

        page.cursorField = "id"

        session = self.getSession ()
        try:
            query = {
                "where": self.soft_delete (),
            }

            if filters:
                query["where"].update (self.filter (filters))

            if orders:
                query.update (self.order (orders))

            return await self.cursor_paginate_all (
                model=User,
                query=query,
                page=page,
                session=session
            )
        finally:
            session.close ()

    @staticmethod
    async def get (userId: str, id: str) -> Optional[User]:
        """
        Args:
            userId (str)
            id (str)
        Returns:
            Optional[User]
        """
        session = UserAdminRepository.getSession ()
        try:
            statement = select (User).where (User.id == id, User.deleted_at == None)
            result = session.exec (statement).first ()
            return result
        finally:
            session.close ()

    @staticmethod
    async def update (userId: str, id: str, data: Dict[str, object]) -> Optional[User]:
        """
        Args:
            userId (str)
            id (str)
            data (Dict[str, object])
        Returns:
            Optional[User]
        """
        session = UserAdminRepository.getSession ()
        try:
            statement = select (User).where (User.id == id, User.deleted_at == None)
            user = session.exec (statement).first ()
            if not user:
                return None
            if "name" in data and data["name"] is not None:
                user.name = data["name"]
            if "email" in data and data["email"] is not None:
                user.email = data["email"]
            if "password" in data and data["password"] is not None:
                user.password = AppAuth.hashPassword (data["password"])
            user.updated_at = datetime.utcnow ()
            session.add (user)
            session.commit ()
            session.refresh (user)
            return user
        finally:
            session.close ()

    @staticmethod
    async def create (userId: str, data: Dict[str, object]) -> Optional[User]:
        """
        Args:
            userId (str)
            data (Dict[str, object])
        Returns:
            Optional[User]
        """
        session = UserAdminRepository.getSession ()
        try:
            user = User (
                id=str (ULID ()),
                name=data.get ("name"),
                email=data.get ("email"),
                password=AppAuth.hashPassword (data.get ("password")),
                email_verified_at=datetime.utcnow (),
                created_at=datetime.utcnow (),
                updated_at=datetime.utcnow ()
            )
            session.add (user)
            session.commit ()
            session.refresh (user)
            return user
        finally:
            session.close ()

    @staticmethod
    async def restore (userId: str, id: str) -> Optional[User]:
        """
        Args:
            userId (str)
            id (str)
        Returns:
            Optional[User]
        """
        session = UserAdminRepository.getSession ()
        try:
            statement = select (User).where (User.id == id)
            user = session.exec (statement).first ()
            if not user:
                return None
            user.deleted_at = None
            user.updated_at = datetime.utcnow ()
            session.add (user)
            session.commit ()
            session.refresh (user)
            return user
        finally:
            session.close ()

    @staticmethod
    async def delete (userId: str, id: str) -> Optional[User]:
        """
        Args:
            userId (str)
            id (str)
        Returns:
            Optional[User]
        """
        session = UserAdminRepository.getSession ()
        try:
            statement = select (User).where (User.id == id, User.deleted_at == None)
            user = session.exec (statement).first ()
            if not user:
                return None
            user.deleted_at = datetime.utcnow ()
            user.updated_at = datetime.utcnow ()
            session.add (user)
            session.commit ()
            session.refresh (user)
            return user
        finally:
            session.close ()

    @staticmethod
    async def verify (userId: str, id: str) -> Optional[User]:
        """
        Args:
            userId (str)
            id (str)
        Returns:
            Optional[User]
        """
        session = UserAdminRepository.getSession ()
        try:
            statement = select (User).where (User.id == id, User.deleted_at == None, User.email_verified_at == None)
            user = session.exec (statement).first ()
            if not user:
                return None
            user.email_verified_at = datetime.utcnow ()
            session.add (user)
            session.commit ()
            session.refresh (user)
            return user
        finally:
            session.close ()

    @staticmethod
    async def forceDelete (id: str) -> Optional[User]:
        """
        Args:
            id (str)
        Returns:
            Optional[User]
        """
        session = UserAdminRepository.getSession ()
        try:
            user = session.exec (select (User).where (User.id == id)).first ()
            if user is None:
                return None

            for notification in session.exec (select (Notification).where (Notification.user_id == id)).all ():
                session.delete (notification)
            for push in session.exec (select (PushSubscription).where (PushSubscription.subscribable_id == id)).all ():
                session.delete (push)
            for token in session.exec (select (PasswordResetToken).where (PasswordResetToken.email == user.email)).all ():
                session.delete (token)
            for link in session.exec (select (ModelHasRole).where (ModelHasRole.model_id == id, ModelHasRole.model_type == "User")).all ():
                session.delete (link)
            profile = session.exec (select (Profile).where (Profile.user_id == id)).first ()
            if profile is not None:
                session.delete (profile)
            session.delete (user)
            session.commit ()
            return user
        except Exception:
            session.rollback ()
            raise
        finally:
            session.close ()
