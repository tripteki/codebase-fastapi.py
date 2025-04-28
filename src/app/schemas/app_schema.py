from strawberry import Schema
from strawberry import type as strawberry_type, field
from strawberry.fastapi import GraphQLRouter
from strawberry.types import Info
from typing import Optional
from src.app.configs.playground_config import PlaygroundConfig
from src.app.configs.app_config import AppConfig
from src.v1.graphql.user.resolvers.mutation import UserMutation
from src.v1.graphql.user.resolvers.query import UserQuery
from src.v1.graphql.user.dtos.type import UserTransformerDto, UserAuthTransformerDto
from src.v1.graphql.user.dtos.input import UserAuthDto
from src.v1.api.user.services.user_auth_service import UserAuthService
from src.v1.api.user.dtos.user_validator_dto import UserAuthDto as UserAuthValidatorDto

def createSchema () -> Schema:
    """
    Args:
    Returns:
        Schema
    """
    @strawberry_type
    class Query:
        @field
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

        @field
        def version (self) -> str:
            """
            Args:
            Returns:
                str
            """
            config = AppConfig.config ()
            return config.app_version

    @strawberry_type
    class Mutation:
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
            request = info.context.get ("request")
            if not request:
                return False
            token = UserAuthService.httpBearerToken (request)
            if not token:
                return False
            try:
                userId = await UserAuthService.validateToken (token)
                if not userId:
                    return False
                await UserAuthService.logout (userId, token)
                return True
            except Exception:
                return False

    return Schema (query=Query, mutation=Mutation)

schema = createSchema ()

def createGraphQLRouter () -> GraphQLRouter:
    """
    Args:
    Returns:
        GraphQLRouter
    """
    config = PlaygroundConfig.config ()
    playgroundPath = config.playground_path
    if not playgroundPath.startswith ("/"):
        playgroundPath = f"/{playgroundPath}"
    return GraphQLRouter (schema, graphql_ide="playground", path=playgroundPath, include_in_schema=False)
