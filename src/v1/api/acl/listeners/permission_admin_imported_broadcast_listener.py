import logging
from src.app.bases.app_event import OnEvent
from src.app.bases.app_realtime import emitToUser
from src.v1.api.log.support.admin_refresh_broadcaster import AdminRefreshBroadcaster
from src.v1.api.acl.events.permission.admin.imported.event import PermissionAdminImportedEvent
from src.v1.api.acl.events.permission.admin.imported_failed.event import PermissionAdminImportedFailedEvent

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
        await emitToUser (event.userId, "v1.acl.permission.admin.imported", {
            "userId": event.userId,
            "filename": event.filename,
            "totalImported": event.totalImported,
            "totalSkipped": event.totalSkipped,
        })
        if event.totalImported > 0:
            await AdminRefreshBroadcaster.broadcast (["permissions"], event.userId)
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
        await emitToUser (event.userId, "v1.acl.permission.admin.imported-failed", {
            "userId": event.userId,
            "filename": event.filename,
            "error": event.error,
        })
    except Exception:
        logger.warning ("event listener failed module=%s", __name__, exc_info=True)
