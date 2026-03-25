"""Provide `StoragePath` related services."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Self, Unpack

from pypaperless.const import EndpointPath, PaperlessResource
from pypaperless.models.filters import StoragePathFilters
from pypaperless.models.storage_paths import StoragePath, StoragePathDraft

from . import mixins
from .base import ResourceService


class StoragePathService(
    ResourceService,
    mixins.SecurableService,
    mixins.CallableService[StoragePath],
    mixins.CreatableService[StoragePathDraft],
    mixins.IterableService[StoragePath],
    mixins.UpdatableService[StoragePath],
    mixins.DeletableService[StoragePath],
):
    """Represent a factory for Paperless `StoragePath` models."""

    _api_path = EndpointPath.STORAGE_PATHS
    _resource = PaperlessResource.STORAGE_PATHS

    _draft_cls = StoragePathDraft
    _resource_cls = StoragePath

    @asynccontextmanager
    async def filter(self, **kwargs: Unpack[StoragePathFilters]) -> AsyncGenerator[Self]:
        """Iterate storage paths with server-side filters.

        See :class:`~pypaperless.models.filters.StoragePathFilters` for all available keys.

        Example::

            async with paperless.storage_paths.filter(name__icontains="archive") as filtered:
                async for sp in filtered:
                    print(sp.path)

        """
        async with self._store_filters(**kwargs) as ctx:
            yield ctx
