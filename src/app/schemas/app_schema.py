from strawberry import Schema
from strawberry import type as strawberry_type, field
from strawberry.fastapi import GraphQLRouter
from strawberry.types import Info
from typing import Optional
from src.app.configs.playground_config import PlaygroundConfig
from src.app.configs.app_config import AppConfig
from src.app.dependencies.app_auth_graphql_dependency import get_current_user_graphql
from src.v1.graphql.user.resolvers.mutation import UserMutation
from src.v1.graphql.user.resolvers.query import UserQuery
from src.v1.graphql.user.dtos.type import UserTransformerDto, UserAuthTransformerDto
from src.v1.graphql.user.dtos.input import UserAuthDto
from src.v1.api.user.services.user_auth_service import UserAuthService
from src.v1.api.user.dtos.user_validator_dto import UserAuthDto as UserAuthValidatorDto

def createSchema () -> Schema:
    """
    Returns:
        Schema
    """
    @strawberry_type
    class Query:
        """
        Query
        """
        @field
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

        @field
        def version (self) -> str:
            """
            Returns:
                str
            """
            config = AppConfig.config ()
            return config.app_version

    @strawberry_type
    class Mutation:
        """
        Mutation
        """
        @field
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

        @field
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
                request = info.context.get ("request")
                token = UserAuthService.httpBearerToken (request) if request else None
                if not token:
                    return False
                await UserAuthService.logout (user.id, token)
                return True
            except Exception:
                return False

    return Schema (query=Query, mutation=Mutation)

schema = createSchema ()

def createGraphQLRouter () -> GraphQLRouter:
    """
    Returns:
        GraphQLRouter
    """
    config = PlaygroundConfig.config ()
    playgroundPath = config.playground_path
    if not playgroundPath.startswith ("/"):
        playgroundPath = f"/{playgroundPath}"
    return GraphQLRouter (schema, graphql_ide="playground", path=playgroundPath, include_in_schema=False)
