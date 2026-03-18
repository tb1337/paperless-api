"""Provide `StoragePath` related services."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Self, Unpack

from pypaperless.const import API_PATH, PaperlessResource
from pypaperless.models.filters import StoragePathFilters
from pypaperless.models.storage_paths import StoragePath, StoragePathDraft

from . import mixins
from .base import ResourceService


class StoragePathService(
    ResourceService,
    mixins.SecurableMixin,
    mixins.CallableMixin[StoragePath],
    mixins.CreatableMixin[StoragePathDraft],
    mixins.IterableMixin[StoragePath],
    mixins.UpdatableMixin[StoragePath],
    mixins.DeletableMixin[StoragePath],
):
    """Represent a factory for Paperless `StoragePath` models."""

    _api_path = API_PATH["storage_paths"]
    _resource = PaperlessResource.STORAGE_PATHS

    _draft_cls = StoragePathDraft
    _resource_cls = StoragePath

    @asynccontextmanager
    async def filter(self, **kwargs: Unpack[StoragePathFilters]) -> AsyncGenerator[Self]:
        """Iterate with server-side filters.

        See :class:`~pypaperless.models.filters.StoragePathFilters` for available keys.
        """
        async with self._store_filters(**kwargs) as ctx:
            yield ctx
