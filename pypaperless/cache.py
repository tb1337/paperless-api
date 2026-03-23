"""Provide the PaperlessCache class."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pypaperless.models.custom_fields import CustomField


class PaperlessCache:
    """In-memory cache for Paperless master data.

    Held by :class:`~pypaperless.runtime.PaperlessRuntime` and accessible to
    services and models via ``runtime.cache``.

    Example::

        async with PaperlessClient("localhost:8000", "token") as paperless:
            fields = paperless.runtime.cache.custom_fields

    """

    def __init__(self) -> None:
        """Initialize an empty :class:`PaperlessCache`."""
        self.custom_fields: dict[int, CustomField] | None = None
