from typing import Optional
from strawberry import type as strawberry_type, field as strawberry_field
from strawberry.types import Info
from src.app.dependencies.app_auth_graphql_dependency import get_current_user_graphql
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
        user = await get_current_user_graphql (info)
        if not user:
            return None
        try:
            result = await UserAuthService.me (user.id)
            return UserTransformerDto.fromModel (result) if result else None
        except Exception:
            return None
