from typing import Optional
from pydantic import BaseModel, Field

class WebPushKeysValidatorDto (BaseModel):
    """
    WebPushKeysValidatorDto (BaseModel)
    """
    p256dh: Optional[str] = Field (default=None, json_schema_extra={"example": "test-p256dh"})
    auth: Optional[str] = Field (default=None, json_schema_extra={"example": "test-auth"})

class WebPushSubscribeValidatorDto (BaseModel):
    """
    WebPushSubscribeValidatorDto (BaseModel)
    """
    endpoint: str = Field (..., json_schema_extra={"example": "https://push.example.test/subscription"})
    keys: Optional[WebPushKeysValidatorDto] = None
    content_encoding: Optional[str] = Field (default=None, json_schema_extra={"example": "aesgcm"})

class WebPushUnsubscribeValidatorDto (BaseModel):
    """
    WebPushUnsubscribeValidatorDto (BaseModel)
    """
    endpoint: str = Field (..., json_schema_extra={"example": "https://push.example.test/subscription"})

class WebPushSuccessTransformerDto (BaseModel):
    """
    WebPushSuccessTransformerDto (BaseModel)
    """
    success: bool = Field (default=True, json_schema_extra={"example": True})
