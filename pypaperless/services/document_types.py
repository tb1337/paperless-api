"""Provide `DocumentType` related services."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Self, Unpack

from pypaperless.const import EndpointPath
from pypaperless.models.document_types import DocumentType, DocumentTypeDraft
from pypaperless.models.filters import DocumentTypeFilters

from . import mixins
from .base import ResourceService


class DocumentTypeService(
    ResourceService,
    mixins.SecurableService,
    mixins.CallableService[DocumentType],
    mixins.CreatableService[DocumentTypeDraft],
    mixins.IterableService[DocumentType],
    mixins.UpdatableService[DocumentType],
    mixins.DeletableService[DocumentType],
):
    """Represent a factory for Paperless `DocumentType` models."""

    _api_path = EndpointPath.DOCUMENT_TYPES

    _draft_cls = DocumentTypeDraft
    _resource_cls = DocumentType

    @asynccontextmanager
    async def filter(self, **kwargs: Unpack[DocumentTypeFilters]) -> AsyncGenerator[Self]:
        """Iterate document types with server-side filters.

        See :class:`~pypaperless.models.filters.DocumentTypeFilters` for all available keys.

        Example::

            async with paperless.document_types.filter(name__icontains="invoice") as filtered:
                async for dt in filtered:
                    print(dt.name)

        """
        async with self._store_filters(**kwargs) as ctx:
            yield ctx
