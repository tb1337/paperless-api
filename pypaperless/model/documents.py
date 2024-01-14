"""Provide the documents class."""

from typing import TYPE_CHECKING, Any

from .base import PaperlessBase

if TYPE_CHECKING:
    from pypaperless import Paperless


class Document(PaperlessBase):
    """Documents provides various methods for handling Paperless Documents."""

    def __call__(self, pk: int):
        """Call."""

        return self.parse({"id": pk}, self._api)

    def __init__(self, api: "Paperless", _data: dict[str, Any] | None = None):
        """Initialize a `Documents` instance."""
        super().__init__(api, _data)
