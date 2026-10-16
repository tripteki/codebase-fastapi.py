from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy import func, or_
from sqlmodel import Session, col, select
from src.app.bases.app_database import AppDatabase
from src.app.repositories.app_repository import OffsetPagination, OffsetPaginationType
from src.v1.api.log.databases.models.activity_model import Activity
from src.v1.api.log.dtos.activity_transformer_dto import ActivityTransformerDto
from src.v1.api.log.support.activity_scope import ActivityScope
from src.v1.api.user.databases.models.user_model import User
from src.v1.api.user.databases.models.profile_model import Profile

SUBJECT_TYPE_ALIASES = {
    "user": "User",
    "role": "Role",
    "permission": "Permission",
    "setting": "Setting",
}

SORTABLE_FIELDS = ("description", "subject_type", "event", "created_at")

class ActivityAdminRepository:
    """
    ActivityAdminRepository
    """

    @staticmethod
    def getSession () -> Session:
        """
        Returns:
            Session
        """
        return Session (AppDatabase.databasePostgresql ())

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
    def _normalizeOrders (orders: Optional[List[Any]]) -> List[tuple[str, str]]:
        """
        Args:
            orders (Optional[List[Any]])
        Returns:
            List[tuple[str, str]]
        """
        normalized: List[tuple[str, str]] = []
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

    @staticmethod
    def _parseDate (value: str, *, endOfDay: bool = False) -> Optional[datetime]:
        """
        Args:
            value (str)
            endOfDay (bool)
        Returns:
            Optional[datetime]
        """
        raw = value.strip ()
        if not raw:
            return None
        try:
            if len (raw) == 10:
                parsed = datetime.strptime (raw, "%Y-%m-%d")
                if endOfDay:
                    return parsed.replace (hour=23, minute=59, second=59)
                return parsed
            return datetime.fromisoformat (raw.replace ("Z", "+00:00")).replace (tzinfo=None)
        except ValueError:
            return None

    async def allOffset (
        self,
        orders: List[Any] = None,
        filters: List[Any] = None,
        page: OffsetPaginationType = None,
        ownerId: Optional[str] = None,
    ) -> OffsetPagination[ActivityTransformerDto]:
        """
        Args:
            orders (List[Any])
            filters (List[Any])
            page (OffsetPaginationType)
            ownerId (Optional[str])
        Returns:
            OffsetPagination[ActivityTransformerDto]
        """
        page = page or OffsetPaginationType (currentPage=1, limitPage=10)
        filterMap = self._normalizeFilters (filters)
        orderPairs = self._normalizeOrders (orders)

        session = self.getSession ()
        try:
            statement = select (Activity)
            countStatement = select (func.count ()).select_from (Activity)

            if ownerId:
                ownCondition = ActivityScope.condition (ownerId)
                statement = statement.where (ownCondition)
                countStatement = countStatement.where (ownCondition)

            q = filterMap.get ("q") or filterMap.get ("search")
            if q:
                pattern = f"%{q}%"
                condition = or_ (
                    col (Activity.description).ilike (pattern),
                    col (Activity.log_name).ilike (pattern),
                    col (Activity.event).ilike (pattern),
                )
                statement = statement.where (condition)
                countStatement = countStatement.where (condition)

            subjectType = filterMap.get ("subject_type")
            if subjectType:
                mapped = SUBJECT_TYPE_ALIASES.get (subjectType.lower (), subjectType)
                statement = statement.where (Activity.subject_type == mapped)
                countStatement = countStatement.where (Activity.subject_type == mapped)

            dateFrom = self._parseDate (filterMap.get ("date_from", ""))
            if dateFrom:
                statement = statement.where (Activity.created_at >= dateFrom)
                countStatement = countStatement.where (Activity.created_at >= dateFrom)

            dateTo = self._parseDate (filterMap.get ("date_to", ""), endOfDay=True)
            if dateTo:
                statement = statement.where (Activity.created_at <= dateTo)
                countStatement = countStatement.where (Activity.created_at <= dateTo)

            causer = filterMap.get ("causer")
            if causer:
                causerIds = session.exec (
                    select (User.id)
                    .outerjoin (Profile, Profile.user_id == User.id)
                    .where (
                        or_ (
                            User.id == causer,
                            col (User.email).ilike (f"%{causer}%"),
                            col (Profile.full_name).ilike (f"%{causer}%"),
                        )
                    )
                ).all ()
                if causerIds:
                    statement = statement.where (Activity.causer_id.in_ (list (causerIds)))
                    countStatement = countStatement.where (Activity.causer_id.in_ (list (causerIds)))
                else:
                    statement = statement.where (Activity.id == "__none__")
                    countStatement = countStatement.where (Activity.id == "__none__")

            for field, direction in orderPairs:
                if field not in SORTABLE_FIELDS:
                    continue
                column = getattr (Activity, field)
                statement = statement.order_by (column.desc () if direction == "desc" else column.asc ())

            total = session.exec (countStatement).one ()
            offset = (page.currentPage - 1) * page.limitPage
            activities = session.exec (statement.offset (offset).limit (page.limitPage)).all ()

            causerIds = [item.causer_id for item in activities if item.causer_id]
            causers: Dict[str, User] = {}
            causerNames: Dict[str, Optional[str]] = {}
            if causerIds:
                for user in session.exec (select (User).where (User.id.in_ (causerIds))).all ():
                    causers[user.id] = user
                for profile in session.exec (
                    select (Profile).where (Profile.user_id.in_ (causerIds))
                ).all ():
                    causerNames[profile.user_id] = profile.full_name

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
                data=[
                    ActivityTransformerDto.fromActivity (
                        item,
                        causer=causers.get (item.causer_id) if item.causer_id else None,
                        causerFullName=causerNames.get (item.causer_id) if item.causer_id else None,
                        withDetails=False,
                    )
                    for item in activities
                ],
            )
        finally:
            session.close ()

    async def findById (self, id: str, ownerId: Optional[str] = None) -> Optional[Activity]:
        """
        Args:
            id (str)
            ownerId (Optional[str])
        Returns:
            Optional[Activity]
        """
        session = self.getSession ()
        try:
            statement = select (Activity).where (Activity.id == id)
            if ownerId:
                statement = statement.where (ActivityScope.condition (ownerId))
            return session.exec (statement).first ()
        finally:
            session.close ()

    async def findCauser (self, causerId: Optional[str]) -> Optional[User]:
        """
        Args:
            causerId (Optional[str])
        Returns:
            Optional[User]
        """
        if not causerId:
            return None
        session = self.getSession ()
        try:
            return session.exec (select (User).where (User.id == causerId)).first ()
        finally:
            session.close ()

    async def findCauserFullName (self, causerId: Optional[str]) -> Optional[str]:
        """
        Args:
            causerId (Optional[str])
        Returns:
            Optional[str]
        """
        if not causerId:
            return None
        session = self.getSession ()
        try:
            profile = session.exec (
                select (Profile).where (Profile.user_id == causerId)
            ).first ()
            return profile.full_name if profile else None
        finally:
            session.close ()
