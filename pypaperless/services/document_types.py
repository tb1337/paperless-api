"""Provide `DocumentType` related services."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Self, Unpack

from pypaperless.const import API_PATH, PaperlessResource
from pypaperless.models.document_types import DocumentType, DocumentTypeDraft
from pypaperless.models.filters import DocumentTypeFilters

from . import mixins
from .base import ServiceBase


class DocumentTypeService(
    ServiceBase,
    mixins.SecurableMixin,
    mixins.CallableMixin[DocumentType],
    mixins.DraftableMixin[DocumentTypeDraft],
    mixins.IterableMixin[DocumentType],
    mixins.UpdatableMixin[DocumentType],
    mixins.DeletableMixin[DocumentType],
):
    """Represent a factory for Paperless `DocumentType` models."""

    _api_path = API_PATH["document_types"]
    _resource = PaperlessResource.DOCUMENT_TYPES

    _draft_cls = DocumentTypeDraft
    _resource_cls = DocumentType

    @asynccontextmanager
    async def filter(self, **kwargs: Unpack[DocumentTypeFilters]) -> AsyncGenerator[Self]:
        """Iterate with server-side filters.

        See :class:`~pypaperless.models.filters.DocumentTypeFilters` for available keys.
        """
        async with self._store_filters(**kwargs) as ctx:
            yield ctx
