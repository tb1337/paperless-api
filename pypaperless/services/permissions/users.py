"""Provide `User` related services."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Self, Unpack

from pypaperless.const import API_PATH, PaperlessResource
from pypaperless.models.filters import UserFilters
from pypaperless.models.permissions.users import User
from pypaperless.services import mixins
from pypaperless.services.base import ResourceService


class UserService(
    ResourceService,
    mixins.CallableMixin[User],
    mixins.IterableMixin[User],
):
    """Represent a factory for Paperless `User` models."""

    _api_path = API_PATH["users"]
    _resource = PaperlessResource.USERS

    _resource_cls = User

    @asynccontextmanager
    async def filter(self, **kwargs: Unpack[UserFilters]) -> AsyncGenerator[Self]:
        """Iterate with server-side filters.

        See :class:`~pypaperless.models.filters.UserFilters` for available keys.
        """
        async with self._store_filters(**kwargs) as ctx:
            yield ctx
