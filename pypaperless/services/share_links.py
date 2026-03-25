"""Provide `ShareLink` service."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Self, Unpack

from pypaperless.const import EndpointPath, PaperlessResource
from pypaperless.models.filters import ShareLinkFilters
from pypaperless.models.share_links import ShareLink, ShareLinkDraft

from . import mixins
from .base import ResourceService


class ShareLinkService(
    ResourceService,
    mixins.CallableService[ShareLink],
    mixins.CreatableService[ShareLinkDraft],
    mixins.IterableService[ShareLink],
    mixins.UpdatableService[ShareLink],
    mixins.DeletableService[ShareLink],
):
    """Represent a factory for Paperless `ShareLink` models."""

    _api_path = EndpointPath.SHARE_LINKS
    _resource = PaperlessResource.SHARE_LINKS

    _draft_cls = ShareLinkDraft
    _resource_cls = ShareLink

    @asynccontextmanager
    async def filter(self, **kwargs: Unpack[ShareLinkFilters]) -> AsyncGenerator[Self]:
        """Iterate share links with server-side filters.

        See :class:`~pypaperless.models.filters.ShareLinkFilters` for all available keys.

        Example::

            async with paperless.share_links.filter(document=42) as filtered:
                async for link in filtered:
                    print(link.slug)

        """
        async with self._store_filters(**kwargs) as ctx:
            yield ctx
