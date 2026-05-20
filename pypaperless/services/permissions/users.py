"""Provide `User` related services."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Self, Unpack

from pypaperless.const import EndpointPath
from pypaperless.models.filters import UserFilters
from pypaperless.models.permissions.users import User
from pypaperless.services import mixins
from pypaperless.services.base import ResourceService


class UserService(
    ResourceService,
    mixins.CallableService[User],
    mixins.IterableService[User],
):
    """Represent a factory for Paperless `User` models."""

    _api_path = EndpointPath.USERS

    _resource_cls = User

    @asynccontextmanager
    async def filter(self, **kwargs: Unpack[UserFilters]) -> AsyncGenerator[Self]:
        """Iterate with server-side filters.

        See :class:`~pypaperless.models.filters.UserFilters` for available keys.
        """
        async with self._store_filters(**kwargs) as ctx:
            yield ctx
