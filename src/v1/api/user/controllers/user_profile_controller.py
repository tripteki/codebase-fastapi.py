import re
from typing import List, Optional
from src.app.dependencies.app_rate_limit import rateLimit
from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from src.app.dependencies.app_auth_api_dependency import get_current_user
from src.app.dtos.app_dto import Status
from src.app.utils.app_response_helper import getStandardResponses
from src.v1.api.user.databases.models.user_model import User
from src.v1.api.user.dtos.user_transformer_dto import UserAccessTransformerDto, UserMeTransformerDto
from src.v1.api.user.dtos.user_validator_dto import UserMeUpdateValidatorDto
from src.v1.api.user.services.user_profile_service import UserProfileService

userProfileRouter = APIRouter (prefix="/api/v1/users", tags=["Users"])

async def parseInterestsFromRequest (request: Request) -> List[str]:
    """
    Args:
        request (Request)
    Returns:
        List[str]
    """
    interests: List[str] = []
    pattern = re.compile (r"^interests(?:\[(\d+)\])?$")
    form = await request.form ()

    for key, value in form.multi_items ():
        if not pattern.match (key):
            continue

        if hasattr (value, "filename"):
            continue

        text = str (value).strip ()
        if text:
            interests.append (text)

    return interests

@userProfileRouter.get (
    "/me",
    status_code=Status.OK,
    dependencies=[rateLimit (times=10, seconds=60)],
    response_model=UserMeTransformerDto,
    responses=getStandardResponses (unauthorized=True, forbidden=True),
)
async def showMe (
    current_user: User = Depends (get_current_user),
) -> UserMeTransformerDto:
    """
    Show Current User Profile
    """
    return await UserProfileService.getMe (current_user.id)

@userProfileRouter.put (
    "/me",
    status_code=Status.OK,
    dependencies=[rateLimit (times=10, seconds=60)],
    response_model=UserMeTransformerDto,
    responses=getStandardResponses (unauthorized=True, forbidden=True, unvalidated=True),
)
async def updateMe (
    dto: UserMeUpdateValidatorDto,
    current_user: User = Depends (get_current_user),
) -> UserMeTransformerDto:
    """
    Update Current User Profile
    """
    return await UserProfileService.updateMe (current_user.id, dto)

@userProfileRouter.post (
    "/me",
    status_code=Status.OK,
    dependencies=[rateLimit (times=10, seconds=60)],
    response_model=UserMeTransformerDto,
    responses=getStandardResponses (unauthorized=True, forbidden=True, unvalidated=True),
)
async def updateMeMultipart (
    request: Request,
    name: str = Form (...),
    email: str = Form (...),
    full_name: Optional[str] = Form (None),
    password: Optional[str] = Form (None),
    password_confirmation: Optional[str] = Form (None),
    avatar: Optional[UploadFile] = File (None),
    current_user: User = Depends (get_current_user),
) -> UserMeTransformerDto:
    """
    Update Current User Profile (multipart)
    """
    interests = await parseInterestsFromRequest (request)
    dto = UserMeUpdateValidatorDto (
        name=name,
        email=email,
        full_name=full_name,
        interests=interests,
        password=password,
        password_confirmation=password_confirmation,
    )
    return await UserProfileService.updateMe (current_user.id, dto, avatar)

@userProfileRouter.get (
    "/me/interests",
    status_code=Status.OK,
    dependencies=[rateLimit (times=10, seconds=60)],
    responses=getStandardResponses (unauthorized=True, forbidden=True),
)
async def interests (
    current_user: User = Depends (get_current_user),
) -> dict:
    """
    Profile Interest Suggestions
    """
    return {"data": await UserProfileService.profileInterests ()}

@userProfileRouter.get (
    "/me/accesses",
    status_code=Status.OK,
    dependencies=[rateLimit (times=10, seconds=60)],
    response_model=UserAccessTransformerDto,
    responses=getStandardResponses (unauthorized=True, forbidden=True),
)
async def accesses (
    current_user: User = Depends (get_current_user),
) -> UserAccessTransformerDto:
    """
    Current User Accesses
    """
    return await UserProfileService.accesses (current_user.id)
