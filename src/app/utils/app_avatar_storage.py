from pathlib import Path
from typing import Optional
from uuid import uuid4
from fastapi import HTTPException, UploadFile, status
from src.v1.api.user.dtos.user_avatar_enum import (
    AVATAR_ALLOWED_EXTENSIONS,
    AVATAR_ALLOWED_MIME_TYPES,
    AVATAR_DIRECTORY,
    AVATAR_MAX_SIZE_BYTES,
)

def validateAvatar (file: UploadFile) -> None:
    """
    Args:
        file (UploadFile)
    Returns:
        None
    """
    extension = Path (file.filename or "").suffix.lower ()
    contentType = (file.content_type or "").lower ()

    if extension not in AVATAR_ALLOWED_EXTENSIONS:
        raise HTTPException (
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=[{
                "type": "value_error",
                "loc": ["body", "avatar"],
                "msg": "Avatar must be a JPEG, PNG, GIF, or WebP image",
                "input": file.filename,
            }],
        )

    if contentType and contentType not in AVATAR_ALLOWED_MIME_TYPES:
        raise HTTPException (
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=[{
                "type": "value_error",
                "loc": ["body", "avatar"],
                "msg": "Avatar must be a JPEG, PNG, GIF, or WebP image",
                "input": file.content_type,
            }],
        )

async def saveAvatar (file: UploadFile) -> str:
    """
    Args:
        file (UploadFile)
    Returns:
        str
    """
    validateAvatar (file)
    content = await file.read ()

    if len (content) > AVATAR_MAX_SIZE_BYTES:
        raise HTTPException (
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=[{
                "type": "value_error",
                "loc": ["body", "avatar"],
                "msg": f"Avatar must not exceed {AVATAR_MAX_SIZE_BYTES // (1024 * 1024)}MB",
                "input": file.filename,
            }],
        )

    AVATAR_DIRECTORY.mkdir (parents=True, exist_ok=True)
    extension = Path (file.filename or "").suffix.lower () or ".jpg"
    filename = f"{uuid4 ().hex}{extension}"
    destination = AVATAR_DIRECTORY / filename
    destination.write_bytes (content)
    return f"avatars/{filename}"

def deleteAvatarIfExists (avatarPath: Optional[str]) -> None:
    """
    Args:
        avatarPath (Optional[str])
    Returns:
        None
    """
    if not avatarPath:
        return

    filePath = Path ("storage/disks/public") / avatarPath.lstrip ("/")
    if filePath.is_file ():
        filePath.unlink ()
