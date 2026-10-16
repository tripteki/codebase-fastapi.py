import logging
from src.app.bases.app_event import OnEvent
from src.app.bases.app_realtime import emitToUser
from src.v1.api.acl.events.role.admin.exported.event import RoleAdminExportedEvent
from src.v1.api.acl.events.role.admin.exported_failed.event import RoleAdminExportedFailedEvent

logger = logging.getLogger (__name__)

@OnEvent ("v1.acl.role.admin.exported")
async def handleRoleAdminExported (event: RoleAdminExportedEvent) -> None:
    """
    Args:
        event (RoleAdminExportedEvent)
    Returns:
        None
    """
    try:
        await emitToUser (event.userId, "v1.acl.role.admin.exported", {
            "userId": event.userId,
            "filename": event.filename,
            "fileUrl": event.fileUrl,
        })
    except Exception:
        logger.warning ("event listener failed module=%s", __name__, exc_info=True)

@OnEvent ("v1.acl.role.admin.exported-failed")
async def handleRoleAdminExportedFailed (event: RoleAdminExportedFailedEvent) -> None:
    """
    Args:
        event (RoleAdminExportedFailedEvent)
    Returns:
        None
    """
    try:
        await emitToUser (event.userId, "v1.acl.role.admin.exported-failed", {
            "userId": event.userId,
            "error": event.error,
        })
    except Exception:
        logger.warning ("event listener failed module=%s", __name__, exc_info=True)
