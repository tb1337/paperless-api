"""Provide `CustomField` service."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Self, Unpack

from pypaperless.const import API_PATH, PaperlessResource
from pypaperless.models.custom_fields import CustomField, CustomFieldDraft
from pypaperless.models.filters import CustomFieldFilters

from . import mixins
from .base import ResourceService


class CustomFieldService(
    ResourceService,
    mixins.CallableMixin[CustomField],
    mixins.CreatableMixin[CustomFieldDraft],
    mixins.IterableMixin[CustomField],
    mixins.UpdatableMixin[CustomField],
    mixins.DeletableMixin[CustomField],
):
    """Represent a factory for Paperless `CustomField` models."""

    _api_path = API_PATH["custom_fields"]
    _resource = PaperlessResource.CUSTOM_FIELDS

    _draft_cls = CustomFieldDraft
    _resource_cls = CustomField

    @asynccontextmanager
    async def filter(self, **kwargs: Unpack[CustomFieldFilters]) -> AsyncGenerator[Self]:
        """Iterate custom fields with server-side filters.

        See :class:`~pypaperless.models.filters.CustomFieldFilters` for all available keys.

        Example::

            async with paperless.custom_fields.filter(name__icontains="amount") as filtered:
                async for cf in filtered:
                    print(cf.name)

        """
        async with self._store_filters(**kwargs) as ctx:
            yield ctx
