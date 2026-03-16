"""Provide `Trash` related services."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Self, Unpack

from pypaperless.const import API_PATH, PaperlessResource
from pypaperless.models.documents import Document
from pypaperless.models.filters import DocumentFilters

from . import mixins
from .base import ServiceBase


class TrashService(
    ServiceBase,
    mixins.IterableMixin[Document],
):
    """Represent a factory for Paperless trashed `Document` models."""

    _api_path = API_PATH["trash"]
    _resource = PaperlessResource.TRASH

    _resource_cls = Document

    @asynccontextmanager
    async def filter(self, **kwargs: Unpack[DocumentFilters]) -> AsyncGenerator[Self]:
        """Iterate with server-side filters.

        See :class:`~pypaperless.models.filters.DocumentFilters` for available keys.
        """
        async with self._store_filters(**kwargs) as ctx:
            yield ctx

    async def restore(self, documents: list[int]) -> None:
        """Restore the given documents from the trash.

        `documents`: A list of document primary keys to restore.
        """
        res = await self._client.request(
            "post", self._api_path, json={"action": "restore", "documents": documents}
        )
        res.raise_for_status()

    async def empty(self, documents: list[int] | None = None) -> None:
        """Permanently delete documents from the trash.

        `documents`: An optional list of document primary keys to delete.
        When ``None``, the entire trash is emptied.
        """
        payload: dict = {"action": "empty"}
        if documents is not None:
            payload["documents"] = documents
        res = await self._client.request("post", self._api_path, json=payload)
        res.raise_for_status()
