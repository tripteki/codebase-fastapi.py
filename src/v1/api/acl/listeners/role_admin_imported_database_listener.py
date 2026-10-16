import logging
from src.app.bases.app_event import OnEvent
from src.app.bases.app_i18n import AppI18n
from src.v1.api.acl.events.role.admin.imported.event import RoleAdminImportedEvent
from src.v1.api.acl.events.role.admin.imported_failed.event import RoleAdminImportedFailedEvent
from src.v1.api.notification.dtos.notification_validator_dto import NotificationCreateValidatorDto
from src.v1.api.notification.services.notification_user_service import NotificationUserService

logger = logging.getLogger (__name__)

@OnEvent ("v1.acl.role.admin.imported")
async def handleRoleAdminImported (event: RoleAdminImportedEvent) -> None:
    """
    Args:
        event (RoleAdminImportedEvent)
    Returns:
        None
    """
    try:
        i18n = AppI18n.i18n ()
        await NotificationUserService.notify (
            event.userId,
            NotificationCreateValidatorDto (
                user_id=event.userId,
                type="role.import.completed",
                data={
                    "filename": event.filename,
                    "totalImported": event.totalImported,
                    "totalSkipped": event.totalSkipped,
                    "message": i18n.t (
                        "_v1_acl.import.completed.message",
                        args={
                            "totalImported": event.totalImported,
                            "totalSkipped": event.totalSkipped,
                        },
                    ),
                },
            ),
        )
    except Exception:
        logger.warning ("event listener failed module=%s", __name__, exc_info=True)

@OnEvent ("v1.acl.role.admin.imported-failed")
async def handleRoleAdminImportedFailed (event: RoleAdminImportedFailedEvent) -> None:
    """
    Args:
        event (RoleAdminImportedFailedEvent)
    Returns:
        None
    """
    try:
        i18n = AppI18n.i18n ()
        await NotificationUserService.notify (
            event.userId,
            NotificationCreateValidatorDto (
                user_id=event.userId,
                type="role.import.failed",
                data={
                    "filename": event.filename,
                    "message": i18n.t ("_v1_acl.import.failed.message"),
                    "error": event.error,
                },
            ),
        )
    except Exception:
        logger.warning ("event listener failed module=%s", __name__, exc_info=True)
