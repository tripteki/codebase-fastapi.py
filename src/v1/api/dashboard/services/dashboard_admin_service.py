from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy import func
from sqlmodel import Session, col, select
from src.app.bases.app_database import AppDatabase
from src.v1.api.dashboard.dtos.dashboard_transformer_dto import (
    DashboardActivityBriefDto,
    DashboardLinksDto,
    DashboardNotificationBriefDto,
    DashboardPeriodDto,
    DashboardTransformerDto,
    DashboardUsersDto,
)
from src.v1.api.log.databases.models.activity_model import Activity
from src.v1.api.log.support.activity_scope import ActivityScope
from src.v1.api.notification.databases.models.notification_model import Notification
from src.v1.api.user.databases.models.acl_model import ModelHasRole, Role
from src.v1.api.user.databases.models.user_model import User
from src.v1.api.user.dtos.user_role_enum import UserRoleEnum
from src.v1.api.user.repositories.user_acl_repository import USER_MODEL_TYPE, UserAclRepository

class DashboardAdminService:
    """
    DashboardAdminService
    """

    @staticmethod
    def _resolveBucket (roles: List[str]) -> str:
        """
        Args:
            roles (List[str])
        Returns:
            str
        """
        if UserRoleEnum.Superadmin in roles:
            return UserRoleEnum.Superadmin.value
        if UserRoleEnum.Admin in roles:
            return UserRoleEnum.Admin.value
        return UserRoleEnum.User.value

    @staticmethod
    def _periodBounds (
        period: str,
        dateFrom: Optional[str],
        dateTo: Optional[str],
    ) -> DashboardPeriodDto:
        """
        Args:
            period (str)
            dateFrom (Optional[str])
            dateTo (Optional[str])
        Returns:
            DashboardPeriodDto
        """
        now = datetime.utcnow ()
        key = (period or "30d").strip ().lower ()
        start: Optional[datetime] = None
        end: Optional[datetime] = now

        if key == "today":
            start = now.replace (hour=0, minute=0, second=0, microsecond=0)
        elif key == "7d":
            start = now - timedelta (days=7)
        elif key == "30d":
            start = now - timedelta (days=30)
        elif key == "custom":
            if dateFrom:
                try:
                    start = datetime.fromisoformat (dateFrom.replace ("Z", "+00:00")).replace (tzinfo=None)
                except ValueError:
                    start = None
            if dateTo:
                try:
                    end = datetime.fromisoformat (dateTo.replace ("Z", "+00:00")).replace (tzinfo=None)
                    if len (dateTo.strip ()) <= 10:
                        end = end.replace (
                            hour=23, minute=59, second=59, microsecond=999999
                        )
                except ValueError:
                    end = now
            key = "custom"
        else:
            key = "30d"
            start = now - timedelta (days=30)

        return DashboardPeriodDto (key=key, date_from=start, date_to=end)

    @staticmethod
    def _createdAtInPeriod (column: Any, period: DashboardPeriodDto) -> list:
        """
        Args:
            column (Any)
            period (DashboardPeriodDto)
        Returns:
            list
        """
        filters = []
        if period.date_from is not None:
            filters.append (col (column) >= period.date_from)
        if period.date_to is not None:
            filters.append (col (column) <= period.date_to)
        return filters

    @staticmethod
    def _session () -> Session:
        """
        Returns:
            Session
        """
        return Session (AppDatabase.databasePostgresql ())

    @staticmethod
    def _recentNotifications (
        session: Session,
        userId: str,
        period: DashboardPeriodDto,
        limit: int = 8,
    ) -> Tuple[List[DashboardNotificationBriefDto], int]:
        """
        Args:
            session (Session)
            userId (str)
            period (DashboardPeriodDto)
            limit (int)
        Returns:
            Tuple[List[DashboardNotificationBriefDto], int]
        """
        periodFilters = DashboardAdminService._createdAtInPeriod (
            Notification.created_at, period
        )
        rows = list (session.exec (
            select (Notification)
            .where (
                Notification.user_id == userId,
                Notification.deleted_at == None,
                *periodFilters,
            )
            .order_by (col (Notification.created_at).desc ())
            .limit (limit)
        ).all ())
        unread = session.exec (
            select (func.count ())
            .select_from (Notification)
            .where (
                Notification.user_id == userId,
                Notification.deleted_at == None,
                Notification.read_at == None,
            )
        ).one ()
        items = []
        for row in rows:
            data = row.data or {}
            items.append (DashboardNotificationBriefDto (
                id=row.id,
                type=row.type,
                title=str (data.get ("title") or "") or None,
                body=str (data.get ("body") or data.get ("message") or "") or None,
                url=str (data.get ("url") or "") or None,
                created_at=row.created_at,
                read_at=row.read_at,
            ))
        return items, int (unread or 0)

    @staticmethod
    def _usersPayload (
        session: Session,
        period: DashboardPeriodDto,
    ) -> DashboardUsersDto:
        """
        Args:
            session (Session)
            period (DashboardPeriodDto)
        Returns:
            DashboardUsersDto
        """
        def countUsers (*conditions: Any) -> int:
            """
            Args:
                *conditions (Any)
            Returns:
                int
            """
            return int (session.exec (
                select (func.count ()).select_from (User).where (*conditions)
            ).one () or 0)

        byRole: Dict[str, int] = {}
        for role in session.exec (select (Role).order_by (Role.name)).all ():
            byRole[role.name] = int (session.exec (
                select (func.count ())
                .select_from (ModelHasRole)
                .join (User, User.id == ModelHasRole.model_id)
                .where (
                    ModelHasRole.role_id == role.id,
                    ModelHasRole.model_type == USER_MODEL_TYPE,
                    User.deleted_at == None,
                )
            ).one () or 0)

        return DashboardUsersDto (
            total=countUsers (),
            active=countUsers (
                User.deleted_at == None,
                User.email_verified_at != None,
            ),
            deactivated=countUsers (User.deleted_at != None),
            unverified=countUsers (
                User.deleted_at == None,
                User.email_verified_at == None,
            ),
            new_in_period=countUsers (
                *DashboardAdminService._createdAtInPeriod (User.created_at, period),
            ),
            by_role=byRole,
        )

    @staticmethod
    def _recentActivities (
        session: Session,
        period: DashboardPeriodDto,
        ownerId: Optional[str],
        limit: int = 8,
    ) -> List[DashboardActivityBriefDto]:
        """
        Args:
            session (Session)
            period (DashboardPeriodDto)
            ownerId (Optional[str])
            limit (int)
        Returns:
            List[DashboardActivityBriefDto]
        """
        conditions = DashboardAdminService._createdAtInPeriod (Activity.created_at, period)
        if ownerId:
            conditions.append (ActivityScope.condition (ownerId))
        rows = list (session.exec (
            select (Activity)
            .where (*conditions)
            .order_by (col (Activity.created_at).desc ())
            .limit (limit)
        ).all ())
        causerIds = [row.causer_id for row in rows if row.causer_id]
        emails: Dict[str, str] = {}
        if causerIds:
            for userId, email in session.exec (
                select (User.id, User.email).where (col (User.id).in_ (causerIds))
            ).all ():
                emails[userId] = email
        return [
            DashboardActivityBriefDto (
                id=row.id,
                description=row.description,
                event=row.event,
                subject_type=row.subject_type,
                subject_id=row.subject_id,
                causer_id=row.causer_id,
                causer_email=emails.get (row.causer_id) if row.causer_id else None,
                created_at=row.created_at,
            )
            for row in rows
        ]

    @staticmethod
    async def get (
        userId: str,
        *,
        period: str = "30d",
        dateFrom: Optional[str] = None,
        dateTo: Optional[str] = None,
    ) -> DashboardTransformerDto:
        """
        Args:
            userId (str)
            period (str)
            dateFrom (Optional[str])
            dateTo (Optional[str])
        Returns:
            DashboardTransformerDto
        """
        permissions, roles = await UserAclRepository.getUserAccesses (userId)
        bucket = DashboardAdminService._resolveBucket (roles)
        periodDto = DashboardAdminService._periodBounds (period, dateFrom, dateTo)
        isSuperadmin = UserRoleEnum.Superadmin in roles
        activityOwnerId = await ActivityScope.ownerIdFor (userId)

        session = DashboardAdminService._session ()
        try:
            recent, unread = DashboardAdminService._recentNotifications (
                session, userId, periodDto
            )
            users = None
            activities: Optional[List[DashboardActivityBriefDto]] = None
            if isSuperadmin or "user.view" in permissions:
                users = DashboardAdminService._usersPayload (session, periodDto)
            if isSuperadmin or "activity.view" in permissions:
                activities = DashboardAdminService._recentActivities (
                    session, periodDto, activityOwnerId
                )

            return DashboardTransformerDto (
                role=bucket,
                period=periodDto,
                users=users,
                recent_activities=activities,
                activities_scope="own" if activityOwnerId else "all",
                recent_notifications=recent,
                unread_notifications=unread,
                links=DashboardLinksDto (),
            )
        finally:
            session.close ()
