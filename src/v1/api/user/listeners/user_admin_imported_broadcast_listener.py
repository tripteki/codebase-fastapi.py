from src.app.bases.app_context import AppContext
from src.app.bases.app_event import OnEvent
from src.v1.api.user.events.user.admin.imported.event import UserAdminImportedEvent
from src.v1.api.user.events.user.admin.imported_failed.event import UserAdminImportedFailedEvent

@OnEvent ("v1.user.admin.imported")
async def handleUserAdminImported (event: UserAdminImportedEvent) -> None:
    """
    Args:
        event (UserAdminImportedEvent)
    Returns:
        None
    """
    try:
        app = AppContext.getApp ()
        if hasattr (app.state, "ws") and app.state.ws:
            await app.state.ws.emit ("v1.user.admin.imported", {
                "userId": event.userId,
                "filename": event.filename,
                "totalImported": event.totalImported,
                "totalSkipped": event.totalSkipped
            })
    except Exception:
        pass

@OnEvent ("v1.user.admin.imported-failed")
async def handleUserAdminImportedFailed (event: UserAdminImportedFailedEvent) -> None:
    """
    Args:
        event (UserAdminImportedFailedEvent)
    Returns:
        None
    """
    try:
        app = AppContext.getApp ()
        if hasattr (app.state, "ws") and app.state.ws:
            await app.state.ws.emit ("v1.user.admin.imported-failed", {
                "userId": event.userId,
                "filename": event.filename,
                "error": event.error
            })
    except Exception:
        pass
