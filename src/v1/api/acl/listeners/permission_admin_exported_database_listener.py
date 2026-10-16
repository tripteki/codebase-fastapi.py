import logging
from src.app.bases.app_event import OnEvent
from src.app.bases.app_i18n import AppI18n
from src.v1.api.acl.events.permission.admin.exported.event import PermissionAdminExportedEvent
from src.v1.api.acl.events.permission.admin.exported_failed.event import PermissionAdminExportedFailedEvent
from src.v1.api.notification.dtos.notification_validator_dto import NotificationCreateValidatorDto
from src.v1.api.notification.services.notification_user_service import NotificationUserService

logger = logging.getLogger (__name__)

@OnEvent ("v1.acl.permission.admin.exported")
async def handlePermissionAdminExported (event: PermissionAdminExportedEvent) -> None:
    """
    Args:
        event (PermissionAdminExportedEvent)
    Returns:
        None
    """
    try:
        i18n = AppI18n.i18n ()
        await NotificationUserService.notify (
            event.userId,
            NotificationCreateValidatorDto (
                user_id=event.userId,
                type="permission.export.completed",
                data={
                    "filename": event.filename,
                    "fileUrl": event.fileUrl,
                    "message": i18n.t ("_v1_acl.export.completed.message"),
                },
            ),
        )
    except Exception:
        logger.warning ("event listener failed module=%s", __name__, exc_info=True)

@OnEvent ("v1.acl.permission.admin.exported-failed")
async def handlePermissionAdminExportedFailed (event: PermissionAdminExportedFailedEvent) -> None:
    """
    Args:
        event (PermissionAdminExportedFailedEvent)
    Returns:
        None
    """
    try:
        i18n = AppI18n.i18n ()
        await NotificationUserService.notify (
            event.userId,
            NotificationCreateValidatorDto (
                user_id=event.userId,
                type="permission.export.failed",
                data={
                    "message": i18n.t ("_v1_acl.export.failed.message"),
                    "error": event.error,
                },
            ),
        )
    except Exception:
        logger.warning ("event listener failed module=%s", __name__, exc_info=True)
