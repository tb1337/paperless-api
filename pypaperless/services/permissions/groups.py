"""Provide `Group` related services."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Self, Unpack

from pypaperless.const import API_PATH, PaperlessResource
from pypaperless.models.filters import GroupFilters
from pypaperless.models.permissions.groups import Group
from pypaperless.services import mixins
from pypaperless.services.base import ServiceBase


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
    async def filter(self, **kwargs: Unpack[GroupFilters]) -> AsyncGenerator[Self]:
        """Iterate with server-side filters.

        See :class:`~pypaperless.models.filters.GroupFilters` for available keys.
        """
        async with self._store_filters(**kwargs) as ctx:
            yield ctx
