from pathlib import Path

AVATAR_DIRECTORY = Path ("storage/disks/public/avatars")
AVATAR_MAX_SIZE_BYTES = 2 * 1024 * 1024
AVATAR_ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
AVATAR_ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
}
