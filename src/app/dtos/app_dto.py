from typing import Optional
from fastapi import status
from pydantic import BaseModel, Field

class Status:
    """
    Status

    Attributes:
        OK (int)
        CREATED (int)
        UNVALIDATED (int)
        UNSIGNED (int)
        UNAUTHORIZED (int)
        UNVERIFIED (int)
    """
    OK = status.HTTP_200_OK
    CREATED = status.HTTP_201_CREATED
    UNVALIDATED = status.HTTP_422_UNPROCESSABLE_ENTITY
    UNSIGNED = status.HTTP_401_UNAUTHORIZED
    UNAUTHORIZED = status.HTTP_401_UNAUTHORIZED
    UNVERIFIED = status.HTTP_403_FORBIDDEN

class Message:
    """
    Message

    Attributes:
        OK (str)
        CREATED (str)
        BAD_REQUEST (str)
        UNAUTHORIZED (str)
        FORBIDDEN (str)
        NOT_FOUND (str)
        UNVALIDATED (str)
        UNSIGNED (str)
        UNVERIFIED (str)
    """
    OK = "Ok"
    CREATED = "Created"
    BAD_REQUEST = "Bad Request"
    UNAUTHORIZED = "Unauthorized"
    FORBIDDEN = "Forbidden"
    NOT_FOUND = "Not Found"
    UNVALIDATED = "Validation Error"
    UNSIGNED = "Not Signed"
    UNVERIFIED = "Not Verified"

class Description:
    """
    Description

    Attributes:
        OK (str)
        CREATED (str)
        BAD_REQUEST (str)
        UNAUTHORIZED_MISSING_TOKEN (str)
        UNAUTHORIZED_INVALID_TOKEN (str)
        FORBIDDEN_INSUFFICIENT_PERMISSIONS (str)
        FORBIDDEN_UNVERIFIED (str)
        NOT_FOUND (str)
        UNVALIDATED (str)
        UNAUTHORIZED (str)
        FORBIDDEN (str)
        IMPORT_STARTED (str)
        EXPORT_STARTED (str)
    """
    OK = "Request successful"
    CREATED = "Resource created successfully"

    BAD_REQUEST = "Bad Request"
    UNAUTHORIZED_MISSING_TOKEN = "Unauthorized - Missing or invalid authentication token"
    UNAUTHORIZED_INVALID_TOKEN = "Unauthorized - Invalid or expired token"
    FORBIDDEN_INSUFFICIENT_PERMISSIONS = "Forbidden - Insufficient permissions"
    FORBIDDEN_UNVERIFIED = "Forbidden - Email verification required"
    NOT_FOUND = "Not Found - Resource not found"
    UNVALIDATED = "Validation Error - Request validation failed"

    UNAUTHORIZED = "Unauthorized - Authentication required"
    FORBIDDEN = "Forbidden - Access denied"

    IMPORT_STARTED = "Import Started Successfully"
    EXPORT_STARTED = "Export Started Successfully"

class BatchPayloadType (BaseModel):
    """
    BatchPayloadType (BaseModel)

    Attributes:
        count (int)
    """
    count: int = Field (..., json_schema_extra={"example": 0})
