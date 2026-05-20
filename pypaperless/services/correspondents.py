"""Provide `Correspondent` related services."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Self, Unpack

from pypaperless.const import EndpointPath
from pypaperless.models.correspondents import Correspondent, CorrespondentDraft
from pypaperless.models.filters import CorrespondentFilters

from . import mixins
from .base import ResourceService


class CorrespondentService(
    ResourceService,
    mixins.SecurableService,
    mixins.CallableService[Correspondent],
    mixins.CreatableService[CorrespondentDraft],
    mixins.IterableService[Correspondent],
    mixins.UpdatableService[Correspondent],
    mixins.DeletableService[Correspondent],
):
    """Represent a factory for Paperless `Correspondent` models."""

    _api_path = EndpointPath.CORRESPONDENTS

    _draft_cls = CorrespondentDraft
    _resource_cls = Correspondent

    @asynccontextmanager
    async def filter(self, **kwargs: Unpack[CorrespondentFilters]) -> AsyncGenerator[Self]:
        """Iterate correspondents with server-side filters.

        See :class:`~pypaperless.models.filters.CorrespondentFilters` for all available keys.

        Example::

            async with paperless.correspondents.filter(name__icontains="acme") as filtered:
                async for c in filtered:
                    print(c.name)

        """
        async with self._store_filters(**kwargs) as ctx:
            yield ctx
