import logging
from src.app.bases.app_event import OnEvent
from src.app.bases.app_realtime import emitToUser
from src.v1.api.log.support.admin_refresh_broadcaster import AdminRefreshBroadcaster
from src.v1.api.acl.events.role.admin.imported.event import RoleAdminImportedEvent
from src.v1.api.acl.events.role.admin.imported_failed.event import RoleAdminImportedFailedEvent

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
        await emitToUser (event.userId, "v1.acl.role.admin.imported", {
            "userId": event.userId,
            "filename": event.filename,
            "totalImported": event.totalImported,
            "totalSkipped": event.totalSkipped,
        })
        if event.totalImported > 0:
            await AdminRefreshBroadcaster.broadcast (["roles"], event.userId)
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
        await emitToUser (event.userId, "v1.acl.role.admin.imported-failed", {
            "userId": event.userId,
            "filename": event.filename,
            "error": event.error,
        })
    except Exception:
        logger.warning ("event listener failed module=%s", __name__, exc_info=True)
