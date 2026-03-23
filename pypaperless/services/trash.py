"""Provide `Trash` related services."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Self, Unpack

from pypaperless.const import API_PATH, PaperlessResource
from pypaperless.models.documents import Document
from pypaperless.models.filters import DocumentFilters

from . import mixins
from .base import ResourceService


class TrashService(
    ResourceService,
    mixins.IterableService[Document],
):
    """Represent a factory for Paperless trashed `Document` models."""

    _api_path = API_PATH["trash"]
    _resource = PaperlessResource.TRASH

    _resource_cls = Document

    @asynccontextmanager
    async def filter(self, **kwargs: Unpack[DocumentFilters]) -> AsyncGenerator[Self]:
        """Iterate trashed documents with server-side filters.

        See :class:`~pypaperless.models.filters.DocumentFilters` for all available keys.

        Example::

            async with paperless.trash.filter(title__icontains="old") as filtered:
                async for doc in filtered:
                    print(doc.title)

        """
        async with self._store_filters(**kwargs) as ctx:
            yield ctx

    async def restore(self, documents: list[int]) -> None:
        """Restore the given documents from the trash.

        Args:
            documents: List of document primary keys to restore.

        Example::

            await paperless.trash.restore([10, 11])

        """
        await self._client.transport.request_json(
            "post", self._api_path, json={"action": "restore", "documents": documents}
        )

    async def empty(self, documents: list[int] | None = None) -> None:
        """Permanently delete documents from the trash.

        Args:
            documents: List of document primary keys to permanently delete.
                       When ``None``, the entire trash is emptied.

        Example::

            await paperless.trash.empty([10, 11])  # specific documents
            await paperless.trash.empty()           # empty entire trash

        """
        payload: dict = {"action": "empty"}
        if documents is not None:
            payload["documents"] = documents
        await self._client.transport.request_json("post", self._api_path, json=payload)
