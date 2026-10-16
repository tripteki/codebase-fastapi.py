from datetime import datetime
from typing import Dict, List, Literal, Optional
from pydantic import BaseModel, Field

class DashboardPeriodDto (BaseModel):
    """
    DashboardPeriodDto (BaseModel)

    Attributes:
        key (str)
        date_from (Optional[datetime])
        date_to (Optional[datetime])
    """
    key: str = "30d"
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None

class DashboardNotificationBriefDto (BaseModel):
    """
    DashboardNotificationBriefDto (BaseModel)

    Attributes:
        id (str)
        type (str)
        title (Optional[str])
        body (Optional[str])
        url (Optional[str])
        created_at (Optional[datetime])
        read_at (Optional[datetime])
    """
    id: str
    type: str
    title: Optional[str] = None
    body: Optional[str] = None
    url: Optional[str] = None
    created_at: Optional[datetime] = None
    read_at: Optional[datetime] = None

class DashboardActivityBriefDto (BaseModel):
    """
    DashboardActivityBriefDto (BaseModel)

    Attributes:
        id (str)
        description (str)
        event (Optional[str])
        subject_type (Optional[str])
        subject_id (Optional[str])
        causer_id (Optional[str])
        causer_email (Optional[str])
        created_at (Optional[datetime])
    """
    id: str
    description: str
    event: Optional[str] = None
    subject_type: Optional[str] = None
    subject_id: Optional[str] = None
    causer_id: Optional[str] = None
    causer_email: Optional[str] = None
    created_at: Optional[datetime] = None

class DashboardUsersDto (BaseModel):
    """
    DashboardUsersDto (BaseModel)

    Attributes:
        total (int)
        active (int)
        deactivated (int)
        unverified (int)
        new_in_period (int)
        by_role (Dict[str, int])
    """
    total: int = 0
    active: int = 0
    deactivated: int = 0
    unverified: int = 0
    new_in_period: int = 0
    by_role: Dict[str, int] = Field (default_factory=dict)

class DashboardLinksDto (BaseModel):
    """
    DashboardLinksDto (BaseModel)

    Attributes:
        users (str)
        activities (str)
        notifications (str)
    """
    users: str = "/admin/users"
    activities: str = "/admin/activities"
    notifications: str = "/notifications"

class DashboardTransformerDto (BaseModel):
    """
    DashboardTransformerDto (BaseModel)

    Attributes:
        role (str)
        period (DashboardPeriodDto)
        users (Optional[DashboardUsersDto])
        recent_activities (Optional[List[DashboardActivityBriefDto]])
        activities_scope (Literal["all", "own"])
        recent_notifications (List[DashboardNotificationBriefDto])
        unread_notifications (int)
        links (DashboardLinksDto)
    """
    role: str
    period: DashboardPeriodDto
    users: Optional[DashboardUsersDto] = None
    recent_activities: Optional[List[DashboardActivityBriefDto]] = None
    activities_scope: Literal["all", "own"] = "all"
    recent_notifications: List[DashboardNotificationBriefDto] = Field (default_factory=list)
    unread_notifications: int = 0
    links: DashboardLinksDto = Field (default_factory=DashboardLinksDto)
