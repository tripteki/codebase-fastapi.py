import logging
from src.app.bases.app_event import OnEvent
from src.app.bases.app_i18n import AppI18n
from src.v1.api.acl.events.permission.admin.imported.event import PermissionAdminImportedEvent
from src.v1.api.acl.events.permission.admin.imported_failed.event import PermissionAdminImportedFailedEvent
from src.v1.api.notification.dtos.notification_validator_dto import NotificationCreateValidatorDto
from src.v1.api.notification.services.notification_user_service import NotificationUserService

logger = logging.getLogger (__name__)

@OnEvent ("v1.acl.permission.admin.imported")
async def handlePermissionAdminImported (event: PermissionAdminImportedEvent) -> None:
    """
    Args:
        event (PermissionAdminImportedEvent)
    Returns:
        None
    """
    try:
        i18n = AppI18n.i18n ()
        await NotificationUserService.notify (
            event.userId,
            NotificationCreateValidatorDto (
                user_id=event.userId,
                type="permission.import.completed",
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

@OnEvent ("v1.acl.permission.admin.imported-failed")
async def handlePermissionAdminImportedFailed (event: PermissionAdminImportedFailedEvent) -> None:
    """
    Args:
        event (PermissionAdminImportedFailedEvent)
    Returns:
        None
    """
    try:
        i18n = AppI18n.i18n ()
        await NotificationUserService.notify (
            event.userId,
            NotificationCreateValidatorDto (
                user_id=event.userId,
                type="permission.import.failed",
                data={
                    "filename": event.filename,
                    "message": i18n.t ("_v1_acl.import.failed.message"),
                    "error": event.error,
                },
            ),
        )
    except Exception:
        logger.warning ("event listener failed module=%s", __name__, exc_info=True)
