from typing import Any, Dict, List
from fastapi import APIRouter, Body, Depends, Request
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from src.app.bases.app_security import security
from src.app.dependencies.app_auth_api_dependency import get_current_user
from src.app.dependencies.app_rate_limit import rateLimit
from src.app.dtos.app_dto import Status
from src.app.utils.app_response_helper import getStandardResponses
from src.v1.api.setting.dtos.setting_transformer_dto import SettingTransformerDto
from src.v1.api.setting.dtos.setting_validator_dto import SettingBatchValidatorDto
from src.v1.api.setting.services.setting_admin_service import SettingAdminService
from src.v1.api.user.databases.models.user_model import User

settingAdminRouter = APIRouter (prefix="/api/v1/admin/settings", tags=["SettingAdmin"])

def _wrap (rows: List[SettingTransformerDto]) -> Dict[str, Any]:
    """
    Args:
        rows (List[SettingTransformerDto])
    Returns:
        Dict[str, Any]
    """
    return {"data": rows}

@settingAdminRouter.get (
    "/",
    status_code=Status.OK,
    dependencies=[rateLimit (times=10, seconds=60), Depends (security)],
    responses=getStandardResponses (unauthorized=True, forbidden=True),
)
async def index (
    current_user: User = Depends (get_current_user),
) -> Dict[str, Any]:
    """
    Index
    """
    return _wrap (await SettingAdminService.all (current_user.id))

@settingAdminRouter.put (
    "/",
    status_code=Status.OK,
    dependencies=[rateLimit (times=10, seconds=60), Depends (security)],
    responses=getStandardResponses (unauthorized=True, forbidden=True, unvalidated=True),
)
async def update (
    dto: SettingBatchValidatorDto = Body (...),
    current_user: User = Depends (get_current_user),
) -> Dict[str, Any]:
    """
    Update
    """
    return _wrap (await SettingAdminService.sync (current_user.id, dto))

@settingAdminRouter.post (
    "/",
    status_code=Status.OK,
    dependencies=[rateLimit (times=10, seconds=60), Depends (security)],
    responses=getStandardResponses (unauthorized=True, forbidden=True, unvalidated=True),
)
async def updateMultipart (
    request: Request,
    current_user: User = Depends (get_current_user),
) -> Dict[str, Any]:
    """
    Update Multipart
    """
    form = await request.form ()
    try:
        payload, files = SettingAdminService.parseMultipartRows (list (form.multi_items ()))
    except ValidationError as error:
        raise RequestValidationError (error.errors ())
    return _wrap (await SettingAdminService.sync (current_user.id, payload, files))
