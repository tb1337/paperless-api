"""Factories."""

from typing import TYPE_CHECKING, Any

from .base import PaperlessBase
from .documents import Document
from .iterators import ResourceIterator

if TYPE_CHECKING:
    from pypaperless import Paperless


class DocumentFactory(PaperlessBase):
    """Helper."""

    def __init__(self, api: "Paperless"):
        """Init."""
        super().__init__(api, None)

    def __call__(self, pk: int) -> Document:
        """Call."""
        return Document(self._api, {"id": pk})

    def all(self, limit: int | None = None, **kwargs: Any) -> ResourceIterator[Document]:
        """All."""
        return ResourceIterator(
            Document,
            self._api,
            f"{self._api.url}/documents",
            limit=limit,
            params=kwargs,
        )
