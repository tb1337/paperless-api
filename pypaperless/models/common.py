"""PyPaperless common types."""

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
    """Represent a subtype of `ShareLink`."""

    ARCHIVE = "archive"
    ORIGINAL = "original"
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls: type, value: object) -> "ShareLinkFileVersionType":  # noqa ARG003
        """Set default member on unknown value."""
        return ShareLinkFileVersionType.UNKNOWN


# workflows
@final
class WorkflowActionType(Enum):
    """Represent a subtype of `Workflow`."""

    ASSIGNMENT = 1
    UNKNOWN = -1

    @classmethod
    def _missing_(cls: type, value: object) -> "WorkflowActionType":  # noqa ARG003
        """Set default member on unknown value."""
        return WorkflowActionType.UNKNOWN


# workflows
@final
class WorkflowTriggerType(Enum):
    """Represent a subtype of `Workflow`."""

    CONSUMPTION = 1
    DOCUMENT_ADDED = 2
    DOCUMENT_UPDATED = 3
    UNKNOWN = -1

    @classmethod
    def _missing_(cls: type, value: object) -> "WorkflowTriggerType":  # noqa ARG003
        """Set default member on unknown value."""
        return WorkflowTriggerType.UNKNOWN


# workflows
@final
class WorkflowTriggerSourceType(Enum):
    """Represent a subtype of `Workflow`."""

    CONSUME_FOLDER = 1
    API_UPLOAD = 2
    MAIL_FETCH = 3
    UNKNOWN = -1

    @classmethod
    def _missing_(cls: type, value: object) -> "WorkflowTriggerSourceType":  # noqa ARG003
        """Set default member on unknown value."""
        return WorkflowTriggerSourceType.UNKNOWN
