from typing import Optional
from src.app.bases.app_event_base import AppEventBase

class UserSecurityNoticeEvent (AppEventBase):
    """
    UserSecurityNoticeEvent (AppEventBase)

    Attributes:
        to (str)
        name (str)
        subject (str)
        line1 (str)
        line2 (Optional[str])
        link (Optional[str])
        linkLabel (Optional[str])
    """
    to: str
    name: str
    subject: str
    line1: str
    line2: Optional[str] = None
    link: Optional[str] = None
    linkLabel: Optional[str] = None
