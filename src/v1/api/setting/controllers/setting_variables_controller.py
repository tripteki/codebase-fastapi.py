from typing import Dict, Optional
from fastapi import APIRouter
from src.app.dependencies.app_rate_limit import rateLimit
from src.app.dtos.app_dto import Status
from src.v1.api.setting.services.setting_admin_service import SettingAdminService

settingVariablesRouter = APIRouter (prefix="/api/v1/settings", tags=["SettingVariables"])

@settingVariablesRouter.get (
    "/variables",
    status_code=Status.OK,
    dependencies=[rateLimit (times=30, seconds=60)],
    response_model=Dict[str, Optional[str]],
)
async def variables () -> Dict[str, Optional[str]]:
    """
    Returns:
        Dict[str, Optional[str]]
    """
    return await SettingAdminService.variables ()
