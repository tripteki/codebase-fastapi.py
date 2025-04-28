from typing import Optional
from strawberry import type as strawberry_type, field as strawberry_field
from strawberry.types import Info
from src.app.bases.app_auth import AppAuth
from src.v1.api.user.services.user_auth_service import UserAuthService
from src.v1.graphql.user.dtos.type import UserTransformerDto

@strawberry_type
class UserQuery:
    """
    UserQuery
    """
    @strawberry_field
    async def me (self, info: Info) -> Optional[UserTransformerDto]:
        """
        Args:
            info (Info)
        Returns:
            Optional[UserTransformerDto]
        """
        request = info.context.get ("request")
        if not request:
            return None
        token = UserAuthService.httpBearerToken (request)
        if not token:
            return None
        try:
            userId = await UserAuthService.validateToken (token)
            if not userId:
                return None
            result = await UserAuthService.me (userId)
            return UserTransformerDto.fromModel (result) if result else None
        except Exception:
            return None
