from typing import Awaitable, Callable, Dict, List, Optional, Tuple
from src.v1.api.acl.services.permission_admin_service import PermissionAdminService
from src.v1.api.acl.services.role_admin_service import RoleAdminService
from src.v1.api.log.services.activity_admin_service import ActivityAdminService
from src.v1.api.search.dtos.search_transformer_dto import (
    SearchGroupTransformerDto,
    SearchItemTransformerDto,
    SearchTransformerDto,
)
from src.v1.api.user.dtos.user_role_enum import UserRoleEnum
from src.v1.api.user.repositories.user_acl_repository import UserAclRepository
from src.v1.api.user.services.user_admin_service import UserAdminService

SEARCH_MIN_CHARS = 2
SEARCH_LIMIT = 5

SearchFetcher = Callable[[str, str], Awaitable[List[SearchItemTransformerDto]]]

class SearchAdminService:
    """
    SearchAdminService
    """

    @staticmethod
    def _page () -> Dict[str, object]:
        """
        Returns:
            Dict[str, object]
        """
        return {"currentPage": 1, "limitPage": SEARCH_LIMIT}

    @staticmethod
    async def _users (userId: str, term: str) -> List[SearchItemTransformerDto]:
        """
        Args:
            userId (str)
            term (str)
        Returns:
            List[SearchItemTransformerDto]
        """
        result = await UserAdminService.all (
            userId,
            None,
            [{"field": "q", "search": term}, {"field": "status", "search": "all"}],
            SearchAdminService._page (),
        )
        items: List[SearchItemTransformerDto] = []
        for user in result.data:
            title = (user.full_name or user.name or "").strip () or user.email
            items.append (SearchItemTransformerDto (
                id=user.id,
                title=title,
                subtitle=user.email if user.email != title else None,
                url=f"/admin/users/{user.id}",
            ))
        return items

    @staticmethod
    async def _roles (userId: str, term: str) -> List[SearchItemTransformerDto]:
        """
        Args:
            userId (str)
            term (str)
        Returns:
            List[SearchItemTransformerDto]
        """
        result = await RoleAdminService.all (None, [{"field": "q", "search": term}], SearchAdminService._page ())
        return [
            SearchItemTransformerDto (
                id=role.id,
                title=role.name,
                subtitle=role.guard_name,
                url=f"/admin/roles/{role.id}",
            )
            for role in result.data
        ]

    @staticmethod
    async def _permissions (userId: str, term: str) -> List[SearchItemTransformerDto]:
        """
        Args:
            userId (str)
            term (str)
        Returns:
            List[SearchItemTransformerDto]
        """
        result = await PermissionAdminService.all (None, [{"field": "q", "search": term}], SearchAdminService._page ())
        return [
            SearchItemTransformerDto (
                id=permission.id,
                title=permission.name,
                subtitle=permission.guard_name,
                url=f"/admin/permissions/{permission.id}",
            )
            for permission in result.data
        ]

    @staticmethod
    async def _activities (userId: str, term: str) -> List[SearchItemTransformerDto]:
        """
        Args:
            userId (str)
            term (str)
        Returns:
            List[SearchItemTransformerDto]
        """
        result = await ActivityAdminService.all (
            userId,
            None,
            [{"field": "q", "search": term}],
            SearchAdminService._page (),
        )
        return [
            SearchItemTransformerDto (
                id=activity.id,
                title=activity.description,
                subtitle=activity.event or None,
                url=f"/admin/activities/{activity.id}",
            )
            for activity in result.data
        ]

    @staticmethod
    def _categories () -> List[Tuple[str, str, SearchFetcher]]:
        """
        Returns:
            List[Tuple[str, str, SearchFetcher]]
        """
        return [
            ("users", "user.view", SearchAdminService._users),
            ("roles", "role.view", SearchAdminService._roles),
            ("permissions", "permission.view", SearchAdminService._permissions),
            ("activities", "activity.view", SearchAdminService._activities),
        ]

    @staticmethod
    async def search (userId: str, query: Optional[str], category: Optional[str]) -> SearchTransformerDto:
        """
        Args:
            userId (str)
            query (Optional[str])
            category (Optional[str])
        Returns:
            SearchTransformerDto
        """
        term = (query or "").strip ()
        selected = (category or "all").strip () or "all"

        if len (term) < SEARCH_MIN_CHARS:
            return SearchTransformerDto (results=[])

        permissions, roles = await UserAclRepository.getUserAccesses (userId)
        isSuperadmin = UserRoleEnum.Superadmin in roles

        results: List[SearchGroupTransformerDto] = []
        for key, permission, fetcher in SearchAdminService._categories ():
            if selected not in ("all", key):
                continue
            if not isSuperadmin and permission not in permissions:
                continue

            items = await fetcher (userId, term)
            if items:
                results.append (SearchGroupTransformerDto (category=key, items=items))

        return SearchTransformerDto (results=results)
