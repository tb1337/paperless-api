"""PyPaperless common non-model types."""

from dataclasses import dataclass
from enum import Enum
from typing import Any, final


# custom_fields
@final
class CustomFieldType(Enum):
    """Represent a subtype of `CustomField`."""

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


# documents
@final
@dataclass(kw_only=True)
class CustomFieldValueType:
    """Represent a subtype of `Document`."""

    field: int | None = None
    value: Any | None = None


# documents
@final
@dataclass(kw_only=True)
class DocumentMetadataType:
    """Represent a subtype of `DocumentMeta`."""

    namespace: str | None = None
    prefix: str | None = None
    key: str | None = None
    value: str | None = None


# mixins/models/data_fields, used for classifiers
@final
class MatchingAlgorithmType(Enum):
    """Represent a subtype of `Correspondent`, `DocumentType`, `StoragePath` and `Tag`."""

    NONE = 0
    ANY = 1
    ALL = 2
    LITERAL = 3
    REGEX = 4
    FUZZY = 5
    AUTO = 6
    UNKNOWN = -1

    @classmethod
    def _missing_(cls: type, value: object) -> "MatchingAlgorithmType":  # noqa ARG003
        """Set default member on unknown value."""
        return MatchingAlgorithmType.UNKNOWN


# saved_views
@final
@dataclass(kw_only=True)
class SavedViewFilterRuleType:
    """Represent a subtype of `SavedView`."""

    rule_type: int | None = None
    value: str | None = None


# share_links
@final
class ShareLinkFileVersionType(Enum):
    """Enum with file version."""

    ARCHIVE = "archive"
    ORIGINAL = "original"
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls: type, value: object) -> "ShareLinkFileVersionType":  # noqa ARG003
        """Set default member on unknown value."""
        return ShareLinkFileVersionType.UNKNOWN
