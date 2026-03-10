"""PyPaperless common types."""

from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from .custom_fields import CustomField


class PaperlessCache(BaseModel):
    """Represent a Paperless cache object."""

    custom_fields: dict[int, "CustomField"] | None = None
