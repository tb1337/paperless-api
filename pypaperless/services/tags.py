"""Provide `Tag` related services."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Self, Unpack

from pypaperless.const import API_PATH, PaperlessResource
from pypaperless.models.filters import TagFilters
from pypaperless.models.tags import Tag, TagDraft

from . import mixins
from .base import ResourceService


class TagService(
    ResourceService,
    mixins.SecurableService,
    mixins.CallableService[Tag],
    mixins.CreatableService[TagDraft],
    mixins.IterableService[Tag],
    mixins.UpdatableService[Tag],
    mixins.DeletableService[Tag],
):
    """Represent a factory for Paperless `Tag` models."""

    _api_path = API_PATH["tags"]
    _resource = PaperlessResource.TAGS

    _draft_cls = TagDraft
    _resource_cls = Tag

    @asynccontextmanager
    async def filter(self, **kwargs: Unpack[TagFilters]) -> AsyncGenerator[Self]:
        """Iterate tags with server-side filters.

        See :class:`~pypaperless.models.filters.TagFilters` for all available keys.

        Example::

            async with paperless.tags.filter(name__icontains="urgent") as filtered:
                async for tag in filtered:
                    print(tag.name)

        """
        async with self._store_filters(**kwargs) as ctx:
            yield ctx
