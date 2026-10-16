import logging
from src.app.bases.app_event import OnEvent
from src.app.bases.app_realtime import emitToUser
from src.app.helpers.datetime_helper import formatAppDatetime
from src.v1.api.user.events.user.admin.activated.event import UserAdminActivatedEvent

logger = logging.getLogger (__name__)

@OnEvent ("v1.user.admin.activated")
async def handleUserAdminActivatedBroadcast (event: UserAdminActivatedEvent) -> None:
    """
    Args:
        event (UserAdminActivatedEvent)
    Returns:
        None
    """
    try:
        await emitToUser (event.id, "v1.user.admin.activated", {
            "id": event.id,
            "name": event.name,
            "email": event.email,
            "email_verified_at": formatAppDatetime (event.email_verified_at),
            "created_at": formatAppDatetime (event.created_at),
            "updated_at": formatAppDatetime (event.updated_at),
            "deleted_at": formatAppDatetime (event.deleted_at)
        })
    except Exception:
        logger.warning ("event listener failed module=%s", __name__, exc_info=True)
