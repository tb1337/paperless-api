"""Provide the documents class."""

from typing import TYPE_CHECKING, Any

from pypaperless.const import API_PATH

from .base import PaperlessModel

if TYPE_CHECKING:
    from pypaperless import Paperless


class Document(PaperlessModel):
    """Documents provides various methods for handling Paperless Documents."""

    api_path = API_PATH["documents_single"]

    def __init__(self, api: "Paperless", _data: dict[str, Any] | None = None):
        """Initialize a `Documents` instance."""
        super().__init__(api, _data)
