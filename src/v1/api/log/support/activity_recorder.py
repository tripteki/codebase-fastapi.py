from datetime import datetime
from typing import Any, Dict, Optional
from ulid import ULID
from sqlmodel import Session
from src.app.bases.app_database import AppDatabase
from src.v1.api.log.databases.models.activity_model import Activity
from src.v1.api.log.support.admin_refresh_broadcaster import AdminRefreshBroadcaster

CAUSER_TYPE_USER = "User"

class ActivityRecorder:
    """
    ActivityRecorder
    """

    @staticmethod
    def log (
        *,
        description: str,
        event: Optional[str] = None,
        logName: str = "default",
        subjectType: Optional[str] = None,
        subjectId: Optional[str] = None,
        causerId: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
        batchUuid: Optional[str] = None,
    ) -> Activity:
        """
        Args:
            description (str)
            event (Optional[str])
            logName (str)
            subjectType (Optional[str])
            subjectId (Optional[str])
            causerId (Optional[str])
            properties (Optional[Dict[str, Any]])
            batchUuid (Optional[str])
        Returns:
            Activity
        """
        session = Session (AppDatabase.databasePostgresql ())
        try:
            activity = ActivityRecorder.logInSession (
                session,
                description=description,
                event=event,
                logName=logName,
                subjectType=subjectType,
                subjectId=subjectId,
                causerId=causerId,
                properties=properties,
                batchUuid=batchUuid,
            )
            session.commit ()
            session.refresh (activity)
            AdminRefreshBroadcaster.scheduleForSubject (subjectType, causerId)
            return activity
        except Exception:
            session.rollback ()
            raise
        finally:
            session.close ()

    @staticmethod
    def logInSession (
        session: Session,
        *,
        description: str,
        event: Optional[str] = None,
        logName: str = "default",
        subjectType: Optional[str] = None,
        subjectId: Optional[str] = None,
        causerId: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
        batchUuid: Optional[str] = None,
    ) -> Activity:
        """
        Args:
            session (Session)
            description (str)
            event (Optional[str])
            logName (str)
            subjectType (Optional[str])
            subjectId (Optional[str])
            causerId (Optional[str])
            properties (Optional[Dict[str, Any]])
            batchUuid (Optional[str])
        Returns:
            Activity
        """
        activity = Activity (
            id=str (ULID ()),
            log_name=logName,
            description=description,
            subject_type=subjectType,
            event=event,
            subject_id=subjectId,
            causer_type=CAUSER_TYPE_USER if causerId else None,
            causer_id=causerId,
            properties=properties,
            batch_uuid=batchUuid,
            created_at=datetime.utcnow (),
            updated_at=datetime.utcnow (),
        )
        session.add (activity)
        session.flush ()
        return activity

    @staticmethod
    def userCreated (causerId: Optional[str], userId: str, attributes: Dict[str, Any]) -> Activity:
        """
        Args:
            causerId (Optional[str])
            userId (str)
            attributes (Dict[str, Any])
        Returns:
            Activity
        """
        return ActivityRecorder.log (
            description="user created",
            event="created",
            subjectType="User",
            subjectId=userId,
            causerId=causerId,
            properties={"attributes": attributes},
        )

    @staticmethod
    def userUpdated (causerId: Optional[str], userId: str, attributes: Dict[str, Any]) -> Activity:
        """
        Args:
            causerId (Optional[str])
            userId (str)
            attributes (Dict[str, Any])
        Returns:
            Activity
        """
        return ActivityRecorder.log (
            description="user updated",
            event="updated",
            subjectType="User",
            subjectId=userId,
            causerId=causerId,
            properties={"attributes": attributes},
        )

    @staticmethod
    def userDeactivated (causerId: Optional[str], userId: str) -> Activity:
        """
        Args:
            causerId (Optional[str])
            userId (str)
        Returns:
            Activity
        """
        return ActivityRecorder.log (
            description="user deactivated",
            event="deactivated",
            subjectType="User",
            subjectId=userId,
            causerId=causerId,
        )

    @staticmethod
    def userActivated (causerId: Optional[str], userId: str) -> Activity:
        """
        Args:
            causerId (Optional[str])
            userId (str)
        Returns:
            Activity
        """
        return ActivityRecorder.log (
            description="user activated",
            event="activated",
            subjectType="User",
            subjectId=userId,
            causerId=causerId,
        )

    @staticmethod
    def userVerified (causerId: Optional[str], userId: str) -> Activity:
        """
        Args:
            causerId (Optional[str])
            userId (str)
        Returns:
            Activity
        """
        return ActivityRecorder.log (
            description="user verified",
            event="verified",
            subjectType="User",
            subjectId=userId,
            causerId=causerId,
        )

    @staticmethod
    def roleCreated (causerId: Optional[str], roleId: str, attributes: Dict[str, Any]) -> Activity:
        """
        Args:
            causerId (Optional[str])
            roleId (str)
            attributes (Dict[str, Any])
        Returns:
            Activity
        """
        return ActivityRecorder.log (
            description="role created",
            event="created",
            subjectType="Role",
            subjectId=roleId,
            causerId=causerId,
            properties={"attributes": attributes},
        )

    @staticmethod
    def roleUpdated (causerId: Optional[str], roleId: str, attributes: Dict[str, Any]) -> Activity:
        """
        Args:
            causerId (Optional[str])
            roleId (str)
            attributes (Dict[str, Any])
        Returns:
            Activity
        """
        return ActivityRecorder.log (
            description="role updated",
            event="updated",
            subjectType="Role",
            subjectId=roleId,
            causerId=causerId,
            properties={"attributes": attributes},
        )

    @staticmethod
    def roleDeleted (causerId: Optional[str], roleId: str, attributes: Dict[str, Any]) -> Activity:
        """
        Args:
            causerId (Optional[str])
            roleId (str)
            attributes (Dict[str, Any])
        Returns:
            Activity
        """
        return ActivityRecorder.log (
            description="role deleted",
            event="deleted",
            subjectType="Role",
            subjectId=roleId,
            causerId=causerId,
            properties={"old": attributes},
        )

    @staticmethod
    def permissionCreated (causerId: Optional[str], permissionId: str, attributes: Dict[str, Any]) -> Activity:
        """
        Args:
            causerId (Optional[str])
            permissionId (str)
            attributes (Dict[str, Any])
        Returns:
            Activity
        """
        return ActivityRecorder.log (
            description="permission created",
            event="created",
            subjectType="Permission",
            subjectId=permissionId,
            causerId=causerId,
            properties={"attributes": attributes},
        )

    @staticmethod
    def permissionUpdated (causerId: Optional[str], permissionId: str, attributes: Dict[str, Any]) -> Activity:
        """
        Args:
            causerId (Optional[str])
            permissionId (str)
            attributes (Dict[str, Any])
        Returns:
            Activity
        """
        return ActivityRecorder.log (
            description="permission updated",
            event="updated",
            subjectType="Permission",
            subjectId=permissionId,
            causerId=causerId,
            properties={"attributes": attributes},
        )

    @staticmethod
    def permissionDeleted (causerId: Optional[str], permissionId: str, attributes: Dict[str, Any]) -> Activity:
        """
        Args:
            causerId (Optional[str])
            permissionId (str)
            attributes (Dict[str, Any])
        Returns:
            Activity
        """
        return ActivityRecorder.log (
            description="permission deleted",
            event="deleted",
            subjectType="Permission",
            subjectId=permissionId,
            causerId=causerId,
            properties={"old": attributes},
        )

    @staticmethod
    def settingCreated (causerId: Optional[str], settingId: str, attributes: Dict[str, Any]) -> Activity:
        """
        Args:
            causerId (Optional[str])
            settingId (str)
            attributes (Dict[str, Any])
        Returns:
            Activity
        """
        return ActivityRecorder.log (
            description="setting created",
            event="created",
            subjectType="Setting",
            subjectId=settingId,
            causerId=causerId,
            properties={"attributes": attributes},
        )

    @staticmethod
    def settingUpdated (causerId: Optional[str], settingId: str, old: Dict[str, Any], attributes: Dict[str, Any]) -> Activity:
        """
        Args:
            causerId (Optional[str])
            settingId (str)
            old (Dict[str, Any])
            attributes (Dict[str, Any])
        Returns:
            Activity
        """
        return ActivityRecorder.log (
            description="setting updated",
            event="updated",
            subjectType="Setting",
            subjectId=settingId,
            causerId=causerId,
            properties={"old": old, "attributes": attributes},
        )

    @staticmethod
    def settingDeleted (causerId: Optional[str], settingId: str, old: Dict[str, Any]) -> Activity:
        """
        Args:
            causerId (Optional[str])
            settingId (str)
            old (Dict[str, Any])
        Returns:
            Activity
        """
        return ActivityRecorder.log (
            description="setting deleted",
            event="deleted",
            subjectType="Setting",
            subjectId=settingId,
            causerId=causerId,
            properties={"old": old},
        )
