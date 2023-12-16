"""Model for custom field resource."""

from dataclasses import dataclass
from typing import Any

from .base import PaperlessModel, PaperlessPost
from .shared import CustomFieldType


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
