from src.app.bases.app_event import OnEvent
from src.app.bases.app_realtime import emitToUser
from src.v1.api.user.events.user.admin.deactivated.event import UserAdminDeactivatedEvent

@OnEvent ("v1.user.admin.deactivated")
async def handleUserAdminDeactivatedBroadcast (event: UserAdminDeactivatedEvent) -> None:
    """
    Args:
        event (UserAdminDeactivatedEvent)
    Returns:
        None
    """
    try:
        await emitToUser (event.id, "v1.user.admin.deactivated", {
            "id": event.id,
            "name": event.name,
            "email": event.email,
            "email_verified_at": str (event.email_verified_at) if event.email_verified_at else None,
            "created_at": str (event.created_at) if event.created_at else None,
            "updated_at": str (event.updated_at) if event.updated_at else None,
            "deleted_at": str (event.deleted_at) if event.deleted_at else None
        })
    except Exception:
        pass
