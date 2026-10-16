from typing import Any, Dict, List, Optional
from fastapi import HTTPException, UploadFile, status
from src.app.bases.app_i18n import AppI18n
from src.app.utils.app_upload_guard import readImageUpload
from src.v1.api.log.support.activity_recorder import ActivityRecorder
from src.v1.api.setting.databases.models.setting_model import Setting
from src.v1.api.setting.dtos.setting_transformer_dto import SettingTransformerDto
from src.v1.api.setting.dtos.setting_validator_dto import SettingBatchValidatorDto, SettingRowValidatorDto
from src.v1.api.setting.repositories.setting_repository import SettingRepository
from src.v1.api.user.dtos.user_role_enum import UserRoleEnum
from src.v1.api.user.repositories.user_acl_repository import UserAclRepository

VARIABLE_KEYS = [
    "APP_NAME",
    "COLOR_PRIMARY",
    "COLOR_SECONDARY",
    "COLOR_TERTIARY",
    "DEFAULT_LOCALE",
]

class SettingAdminService:
    """
    SettingAdminService

    Attributes:
        repository (SettingRepository)
    """
    repository = SettingRepository ()

    @staticmethod
    def _attributes (setting: Setting) -> Dict[str, Any]:
        """
        Args:
            setting (Setting)
        Returns:
            Dict[str, Any]
        """
        return {
            "key": setting.key,
            "value_kind": setting.value_kind,
            "value": setting.value,
        }

    @staticmethod
    async def assertSystemAccess (userId: str) -> None:
        """
        Args:
            userId (str)
        Returns:
            None
        """
        role = await UserAclRepository.getUserRole (userId)
        if role not in UserRoleEnum.systemSettings ():
            i18n = AppI18n.i18n ()
            raise HTTPException (
                status_code=status.HTTP_403_FORBIDDEN,
                detail=i18n.t ("_v1_setting.forbidden"),
            )

    @staticmethod
    async def all (userId: str) -> List[SettingTransformerDto]:
        """
        Args:
            userId (str)
        Returns:
            List[SettingTransformerDto]
        """
        await SettingAdminService.assertSystemAccess (userId)
        settings = await SettingAdminService.repository.all ()
        return [SettingTransformerDto.fromSetting (item) for item in settings]

    @staticmethod
    async def variables () -> Dict[str, Optional[str]]:
        """
        Returns:
            Dict[str, Optional[str]]
        """
        result: Dict[str, Optional[str]] = {}
        for key in VARIABLE_KEYS:
            setting = await SettingAdminService.repository.findByKey (key)
            result[key] = setting.value if setting else None
        return result

    @staticmethod
    async def sync (
        userId: str,
        payload: SettingBatchValidatorDto,
        files: Optional[Dict[int, UploadFile]] = None,
    ) -> List[SettingTransformerDto]:
        """
        Args:
            userId (str)
            payload (SettingBatchValidatorDto)
            files (Optional[Dict[int, UploadFile]])
        Returns:
            List[SettingTransformerDto]
        """
        await SettingAdminService.assertSystemAccess (userId)
        files = files or {}
        deletes: List[str] = []
        writes: List[tuple[int, SettingRowValidatorDto, str, str]] = []
        seenKeys: set[str] = set ()

        for index, row in enumerate (payload.rows):
            key = (row.key or "").strip ().upper ()
            valueKind = "file" if row.value_kind == "file" else "text"
            value = (row.value or "").strip ()

            if row.id and key == "":
                deletes.append (row.id)
                continue

            if key == "" and value == "" and files.get (index) is None:
                continue

            if key == "":
                i18n = AppI18n.i18n ()
                raise HTTPException (
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=i18n.t ("_v1_setting.key_required"),
                )

            if key in seenKeys:
                i18n = AppI18n.i18n ()
                raise HTTPException (
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=i18n.t ("_v1_setting.key_duplicate"),
                )
            seenKeys.add (key)
            writes.append ((index, row, key, valueKind))

        uploads: Dict[int, tuple[bytes, str]] = {}
        for index, row, key, valueKind in writes:
            file = files.get (index)
            if valueKind == "file" and file is not None:
                uploads[index] = await readImageUpload (file, ("rows", index, "file"), allowIcon=True)

        for id in deletes:
            existing = await SettingAdminService.repository.findById (id)
            if existing is None:
                continue
            await SettingAdminService.repository.softDelete (id)
            ActivityRecorder.settingDeleted (
                causerId=userId,
                settingId=existing.id,
                old=SettingAdminService._attributes (existing),
            )

        for index, row, key, valueKind in writes:
            previous = await SettingAdminService.repository.findById (row.id) if row.id else None
            previous = previous or await SettingAdminService.repository.findByKey (key)
            old = SettingAdminService._attributes (previous) if previous else None

            storedValue = (row.value or "").strip ()
            if index in uploads:
                storedValue = await SettingRepository.saveFile (*uploads[index])
            elif valueKind == "file" and previous and previous.id == row.id and previous.value_kind == "file":
                storedValue = previous.value or storedValue

            setting = await SettingAdminService.repository.upsert (
                id=row.id,
                key=key,
                value=storedValue or None,
                valueKind=valueKind,
            )
            attributes = SettingAdminService._attributes (setting)
            if old is None:
                ActivityRecorder.settingCreated (causerId=userId, settingId=setting.id, attributes=attributes)
            elif old != attributes:
                ActivityRecorder.settingUpdated (causerId=userId, settingId=setting.id, old=old, attributes=attributes)

        return await SettingAdminService.all (userId)

    @staticmethod
    def parseMultipartRows (formItems: List[tuple]) -> tuple[SettingBatchValidatorDto, Dict[int, UploadFile]]:
        """
        Args:
            formItems (List[tuple])
        Returns:
            tuple[SettingBatchValidatorDto, Dict[int, UploadFile]]
        """
        rowsMap: Dict[int, Dict[str, Any]] = {}
        files: Dict[int, UploadFile] = {}

        for key, value in formItems:
            if not str (key).startswith ("rows["):
                continue
            try:
                left = str (key).split ("[", 1)[1]
                indexStr, rest = left.split ("]", 1)
                index = int (indexStr)
                field = rest.strip ("[]")
            except Exception:
                continue

            bucket = rowsMap.setdefault (index, {})
            if field == "file" and hasattr (value, "filename"):
                files[index] = value
            else:
                bucket[field] = str (value) if value is not None else None

        rows = [
            SettingRowValidatorDto (
                id=rowsMap[i].get ("id"),
                key=rowsMap[i].get ("key"),
                value=rowsMap[i].get ("value"),
                value_kind="file" if rowsMap[i].get ("value_kind") == "file" else "text",
            )
            for i in sorted (rowsMap.keys ())
        ]
        return SettingBatchValidatorDto (rows=rows), files
