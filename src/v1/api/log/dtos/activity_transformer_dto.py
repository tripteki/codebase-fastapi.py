from datetime import datetime
from typing import Any, Dict, Optional
from typing_extensions import Self
from pydantic import BaseModel, EmailStr, Field
from src.v1.api.log.databases.models.activity_model import Activity
from src.v1.api.user.databases.models.user_model import User

class ActivityCauserTransformerDto (BaseModel):
    """
    ActivityCauserTransformerDto (BaseModel)

    Attributes:
        id (str)
        full_name (Optional[str])
        email (EmailStr)
    """
    id: str = Field (..., json_schema_extra={"example": "string"})
    full_name: Optional[str] = Field (None, json_schema_extra={"example": "Admin Name"})
    email: EmailStr = Field (..., json_schema_extra={"example": "string"})

class ActivityTransformerDto (BaseModel):
    """
    ActivityTransformerDto (BaseModel)

    Attributes:
        id (str)
        log_name (Optional[str])
        description (str)
        subject_type (Optional[str])
        subject_type_label (Optional[str])
        subject_id (Optional[str])
        event (Optional[str])
        causer_type (Optional[str])
        causer_id (Optional[str])
        properties (Optional[Dict[str, Any]])
        batch_uuid (Optional[str])
        created_at (datetime)
        updated_at (datetime)
        causer (Optional[ActivityCauserTransformerDto])
    """
    id: str = Field (..., json_schema_extra={"example": "string"})
    log_name: Optional[str] = Field (None, json_schema_extra={"example": "default"})
    description: str = Field (..., json_schema_extra={"example": "user created"})
    subject_type: Optional[str] = Field (None, json_schema_extra={"example": "User"})
    subject_type_label: Optional[str] = Field (None, json_schema_extra={"example": "User"})
    subject_id: Optional[str] = Field (None, json_schema_extra={"example": "string"})
    event: Optional[str] = Field (None, json_schema_extra={"example": "created"})
    causer_type: Optional[str] = Field (None, json_schema_extra={"example": "User"})
    causer_id: Optional[str] = Field (None, json_schema_extra={"example": "string"})
    properties: Optional[Dict[str, Any]] = Field (None, json_schema_extra={"example": {}})
    batch_uuid: Optional[str] = Field (None, json_schema_extra={"example": None})
    created_at: datetime = Field (..., json_schema_extra={"example": "string"})
    updated_at: datetime = Field (..., json_schema_extra={"example": "string"})
    causer: Optional[ActivityCauserTransformerDto] = Field (None, json_schema_extra={"example": None})

    @staticmethod
    def fromActivity (
        activity: Activity,
        *,
        causer: Optional[User] = None,
        causerFullName: Optional[str] = None,
        withDetails: bool = False,
    ) -> Self:
        """
        Args:
            activity (Activity)
            causer (Optional[User])
            causerFullName (Optional[str])
            withDetails (bool)
        Returns:
            ActivityTransformerDto
        """
        causerDto = None
        if causer is not None:
            causerDto = ActivityCauserTransformerDto (
                id=causer.id,
                full_name=(causerFullName or "").strip () or None,
                email=causer.email,
            )

        return ActivityTransformerDto (
            id=activity.id,
            log_name=activity.log_name,
            description=activity.description,
            subject_type=activity.subject_type,
            subject_type_label=activity.subject_type,
            subject_id=activity.subject_id,
            event=activity.event,
            causer_type=activity.causer_type,
            causer_id=activity.causer_id,
            properties=activity.properties if withDetails else None,
            batch_uuid=activity.batch_uuid,
            created_at=activity.created_at,
            updated_at=activity.updated_at,
            causer=causerDto,
        )
