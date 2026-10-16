from pathlib import Path
from typing import Optional
from uuid import uuid4
from fastapi import HTTPException, UploadFile, status
from src.app.bases.app_i18n import AppI18n
from src.app.utils.app_upload_guard import readImageUpload
from src.v1.api.user.dtos.user_avatar_enum import (
    AVATAR_ALLOWED_EXTENSIONS,
    AVATAR_ALLOWED_MIME_TYPES,
    AVATAR_DIRECTORY,
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
                "msg": AppI18n.i18n ().t ("_app.upload.image_type"),
                "input": file.filename,
                "ctx": {},
            }],
        )

    if contentType and contentType not in AVATAR_ALLOWED_MIME_TYPES:
        raise HTTPException (
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=[{
                "type": "value_error",
                "loc": ["body", "avatar"],
                "msg": AppI18n.i18n ().t ("_app.upload.image_type"),
                "input": file.content_type,
                "ctx": {},
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
    content, extension = await readImageUpload (file, "avatar")
    AVATAR_DIRECTORY.mkdir (parents=True, exist_ok=True)
    filename = f"{uuid4 ().hex}{extension}"
    (AVATAR_DIRECTORY / filename).write_bytes (content)
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
