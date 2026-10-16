import logging
from src.app.bases.app_event import OnEvent
from src.app.bases.app_realtime import emitToUser
from src.v1.api.acl.events.permission.admin.exported.event import PermissionAdminExportedEvent
from src.v1.api.acl.events.permission.admin.exported_failed.event import PermissionAdminExportedFailedEvent

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
        await emitToUser (event.userId, "v1.acl.permission.admin.exported", {
            "userId": event.userId,
            "filename": event.filename,
            "fileUrl": event.fileUrl,
        })
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
        await emitToUser (event.userId, "v1.acl.permission.admin.exported-failed", {
            "userId": event.userId,
            "error": event.error,
        })
    except Exception:
        logger.warning ("event listener failed module=%s", __name__, exc_info=True)
