"""Model for custom field resource."""

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .base import PaperlessModel, PaperlessPost


class CustomFieldType(Enum):
    """Enum with custom field types."""

    STRING = "string"
    BOOLEAN = "boolean"
    INTEGER = "integer"
    FLOAT = "float"
    MONETARY = "monetary"
    DATE = "date"
    URL = "url"
    DOCUMENT_LINK = "documentlink"
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls: type, value: object) -> "CustomFieldType":  # noqa ARG003
        """Set default member on unknown value."""
        return CustomFieldType.UNKNOWN


@dataclass(kw_only=True)
class CustomFieldValue(PaperlessModel):
    """Represent a custom field value mapping on the Paperless api."""

    field: int | None = None
    value: Any | None = None


@dataclass(kw_only=True)
class CustomField(PaperlessModel):
    """Represent a custom field resource on the Paperless api."""

    id: int | None = None
    name: str | None = None
    data_type: CustomFieldType | None = None


@dataclass(kw_only=True)
class CustomFieldPost(PaperlessPost):
    """Attributes to send when creating a custom field on the Paperless api."""

    name: str
    data_type: CustomFieldType
