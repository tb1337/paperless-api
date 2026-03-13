"""Provide `Group` and `User` services."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Self, Unpack

from pypaperless.const import API_PATH, PaperlessResource
from pypaperless.models.filters import GroupFilters, UserFilters
from pypaperless.models.permissions import Group, User

from . import mixins
from .base import ServiceBase


class GroupService(
    ServiceBase,
    mixins.CallableMixin[Group],
    mixins.IterableMixin[Group],
):
    """Represent a factory for Paperless `Group` models."""

    _api_path = API_PATH["groups"]
    _resource = PaperlessResource.GROUPS

    _resource_cls = Group

    @asynccontextmanager
    async def reduce(self, **kwargs: Unpack[GroupFilters]) -> AsyncGenerator[Self, None]:
        """Iterate with server-side filters.

        See :class:`~pypaperless.models.filters.GroupFilters` for available keys.
        """
        async with self._store_filters(**kwargs) as ctx:
            yield ctx


class UserService(
    ServiceBase,
    mixins.CallableMixin[User],
    mixins.IterableMixin[User],
):
    """Represent a factory for Paperless `User` models."""

    _api_path = API_PATH["users"]
    _resource = PaperlessResource.USERS

    _resource_cls = User

    @asynccontextmanager
    async def reduce(self, **kwargs: Unpack[UserFilters]) -> AsyncGenerator[Self, None]:
        """Iterate with server-side filters.

        See :class:`~pypaperless.models.filters.UserFilters` for available keys.
        """
        async with self._store_filters(**kwargs) as ctx:
            yield ctx
