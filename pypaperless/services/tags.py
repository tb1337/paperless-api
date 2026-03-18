"""Provide `Tag` related services."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Self, Unpack

from pypaperless.const import API_PATH, PaperlessResource
from pypaperless.models.filters import TagFilters
from pypaperless.models.tags import Tag, TagDraft

from . import mixins
from .base import ServiceBase


class TagService(
    ServiceBase,
    mixins.SecurableMixin,
    mixins.CallableMixin[Tag],
    mixins.CreatableMixin[TagDraft],
    mixins.IterableMixin[Tag],
    mixins.UpdatableMixin[Tag],
    mixins.DeletableMixin[Tag],
):
    """Represent a factory for Paperless `Tag` models."""

    _api_path = API_PATH["tags"]
    _resource = PaperlessResource.TAGS

    _draft_cls = TagDraft
    _resource_cls = Tag

    @asynccontextmanager
    async def filter(self, **kwargs: Unpack[TagFilters]) -> AsyncGenerator[Self]:
        """Iterate with server-side filters.

        See :class:`~pypaperless.models.filters.TagFilters` for available keys.
        """
        async with self._store_filters(**kwargs) as ctx:
            yield ctx
