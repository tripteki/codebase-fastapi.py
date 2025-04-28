from strawberry import type as strawberry_type, field as strawberry_field
from strawberry.types import Info
from src.app.dependencies.app_auth_graphql_dependency import get_current_user_graphql
from src.v1.api.user.dtos.user_validator_dto import UserAuthDto as UserAuthValidatorDto
from src.v1.api.user.services.user_auth_service import UserAuthService
from src.v1.graphql.user.dtos.input import UserAuthDto
from src.v1.graphql.user.dtos.type import UserAuthTransformerDto

@strawberry_type
class UserMutation:
    """
    UserMutation
    """
    @strawberry_field
    async def login (self, inputs: UserAuthDto, info: Info) -> UserAuthTransformerDto:
        """
        Args:
            inputs (UserAuthDto)
            info (Info)
        Returns:
            UserAuthTransformerDto
        """
        dto = UserAuthValidatorDto (
            identifierKey=inputs.identifierKey,
            identifierValue=inputs.identifierValue,
            password=inputs.password
        )
        result = await UserAuthService.login (dto)
        return UserAuthTransformerDto (
            accessTokenTtl=float (result.accessTokenTtl) if result.accessTokenTtl else None,
            refreshTokenTtl=float (result.refreshTokenTtl) if result.refreshTokenTtl else None,
            accessToken=result.accessToken,
            refreshToken=result.refreshToken
        )

    @strawberry_field
    async def logout (self, info: Info) -> bool:
        """
        Args:
            info (Info)
        Returns:
            bool
        """
        user = await get_current_user_graphql (info)
        if not user:
            return False
        try:
            from strawberry.types import Info
            request = info.context.get ("request")
            token = UserAuthService.httpBearerToken (request) if request else None
            if not token:
                return False
            await UserAuthService.logout (user.id, token)
            return True
        except Exception:
            return False
