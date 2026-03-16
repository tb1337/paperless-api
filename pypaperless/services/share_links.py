"""Provide `ShareLink` service."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Self, Unpack

from pypaperless.const import API_PATH, PaperlessResource
from pypaperless.models.filters import ShareLinkFilters
from pypaperless.models.share_links import ShareLink, ShareLinkDraft

from . import mixins
from .base import ServiceBase


class ShareLinkService(
    ServiceBase,
    mixins.CallableMixin[ShareLink],
    mixins.DraftableMixin[ShareLinkDraft],
    mixins.IterableMixin[ShareLink],
    mixins.UpdatableMixin[ShareLink],
    mixins.DeletableMixin[ShareLink],
):
    """Represent a factory for Paperless `ShareLink` models."""

    _api_path = API_PATH["share_links"]
    _resource = PaperlessResource.SHARE_LINKS

    _draft_cls = ShareLinkDraft
    _resource_cls = ShareLink

    @asynccontextmanager
    async def filter(self, **kwargs: Unpack[ShareLinkFilters]) -> AsyncGenerator[Self]:
        """Iterate with server-side filters.

        See :class:`~pypaperless.models.filters.ShareLinkFilters` for available keys.
        """
        async with self._store_filters(**kwargs) as ctx:
            yield ctx
