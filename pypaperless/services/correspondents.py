"""Provide `Correspondent` related services."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Self, Unpack

from pypaperless.const import API_PATH, PaperlessResource
from pypaperless.models.correspondents import Correspondent, CorrespondentDraft
from pypaperless.models.filters import CorrespondentFilters

from . import mixins
from .base import ServiceBase


class CorrespondentService(
    ServiceBase,
    mixins.SecurableMixin,
    mixins.CallableMixin[Correspondent],
    mixins.DraftableMixin[CorrespondentDraft],
    mixins.IterableMixin[Correspondent],
    mixins.UpdatableMixin[Correspondent],
    mixins.DeletableMixin[Correspondent],
):
    """Represent a factory for Paperless `Correspondent` models."""

    _api_path = API_PATH["correspondents"]
    _resource = PaperlessResource.CORRESPONDENTS

    _draft_cls = CorrespondentDraft
    _resource_cls = Correspondent

    @asynccontextmanager
    async def reduce(self, **kwargs: Unpack[CorrespondentFilters]) -> AsyncGenerator[Self, None]:
        """Iterate with server-side filters.

        See :class:`~pypaperless.models.filters.CorrespondentFilters` for available keys.
        """
        async with self._store_filters(**kwargs) as ctx:
            yield ctx
