"""Provide `ShareLinkBundle` service."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Self, Unpack

from pypaperless.const import EndpointPath
from pypaperless.models.filters import ShareLinkBundleFilters
from pypaperless.models.share_links.bundle import ShareLinkBundle, ShareLinkBundleDraft
from pypaperless.services import mixins
from pypaperless.services.base import ResourceService


class ShareLinkBundleService(
    ResourceService,
    mixins.CallableService[ShareLinkBundle],
    mixins.CreatableService[ShareLinkBundleDraft],
    mixins.IterableService[ShareLinkBundle],
    mixins.UpdatableService[ShareLinkBundle],
    mixins.DeletableService[ShareLinkBundle],
):
    """Represent a factory for Paperless ``ShareLinkBundle`` models."""

    _api_path = EndpointPath.SHARE_LINK_BUNDLES

    _draft_cls = ShareLinkBundleDraft
    _resource_cls = ShareLinkBundle

    @asynccontextmanager
    async def filter(self, **kwargs: Unpack[ShareLinkBundleFilters]) -> AsyncGenerator[Self]:
        """Iterate share link bundles with server-side filters.

        See :class:`~pypaperless.models.filters.ShareLinkBundleFilters` for all available keys.

        Example::

            async with paperless.share_link_bundles.filter(status="ready") as filtered:
                async for bundle in filtered:
                    print(bundle.slug)

        """
        async with self._store_filters(**kwargs) as ctx:
            yield ctx

    async def rebuild(self, bundle_id: int) -> ShareLinkBundle:
        """Trigger a rebuild of a share link bundle.

        Resets and re-queues the bundle for processing. Returns the updated bundle.

        Args:
            bundle_id: Primary key of the bundle to rebuild.

        Example::

            bundle = await paperless.share_link_bundles.rebuild(42)
            print(bundle.status)

        """
        api_path = EndpointPath.SHARE_LINK_BUNDLES_REBUILD.format(pk=bundle_id)
        data = await self._runtime.transport.post(api_path, json={})
        return ShareLinkBundle.from_data(self._runtime, data)
