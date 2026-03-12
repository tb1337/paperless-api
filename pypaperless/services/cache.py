"""Provide a cache service for PyPaperless."""

from typing import TYPE_CHECKING

from .base import PaperlessBase

if TYPE_CHECKING:
    from pypaperless import Paperless
    from pypaperless.models.custom_fields import CustomField


class CacheService(PaperlessBase):
    """Cache for Paperless master data, accessible via `Paperless.cache`."""

    def __init__(self, client: "Paperless") -> None:
        """Initialize a `CacheService` instance."""
        super().__init__(client)
        self.custom_fields: dict[int, CustomField] | None = None
