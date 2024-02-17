"""PyPaperless common types."""

from dataclasses import dataclass, field
from enum import Enum, StrEnum
from typing import Any


# custom_fields
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
@dataclass(kw_only=True)
class CustomFieldValueType:
    """Represent a subtype of `Document`."""

    field: int | None = None
    value: Any | None = None


# documents
@dataclass(kw_only=True)
class DocumentMetadataType:
    """Represent a subtype of `DocumentMeta`."""

    namespace: str | None = None
    prefix: str | None = None
    key: str | None = None
    value: str | None = None


# documents
@dataclass(kw_only=True)
class DocumentSearchHitType:
    """Represent a subtype of `Document`."""

    score: float | None = None
    highlights: str | None = None
    note_highlights: str | None = None
    rank: int | None = None


# mixins/models/data_fields, used for classifiers
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


# mixins/models/securable
@dataclass(kw_only=True)
class PermissionSetType:
    """Represent a Paperless permission set."""

    users: list[int] = field(default_factory=list)
    groups: list[int] = field(default_factory=list)


# mixins/models/securable
@dataclass(kw_only=True)
class PermissionTableType:
    """Represent a Paperless permissions type."""

    view: PermissionSetType = field(default_factory=PermissionSetType)
    change: PermissionSetType = field(default_factory=PermissionSetType)


# documents
class RetrieveFileMode(StrEnum):
    """Represent a subtype of `DownloadedDocument`."""

    DOWNLOAD = "download"
    PREVIEW = "preview"
    THUMBNAIL = "thumb"


# saved_views
@dataclass(kw_only=True)
class SavedViewFilterRuleType:
    """Represent a subtype of `SavedView`."""

    rule_type: int | None = None
    value: str | None = None


# share_links
class ShareLinkFileVersionType(Enum):
    """Represent a subtype of `ShareLink`."""

    ARCHIVE = "archive"
    ORIGINAL = "original"
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls: type, value: object) -> "ShareLinkFileVersionType":  # noqa ARG003
        """Set default member on unknown value."""
        return ShareLinkFileVersionType.UNKNOWN


# tasks
class TaskStatusType(Enum):
    """Represent a subtype of `Task`."""

    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def _missing_(cls: type, value: object) -> "TaskStatusType":  # noqa ARG003
        """Set default member on unknown value."""
        return TaskStatusType.UNKNOWN


# workflows
class WorkflowActionType(Enum):
    """Represent a subtype of `Workflow`."""

    ASSIGNMENT = 1
    UNKNOWN = -1

    @classmethod
    def _missing_(cls: type, value: object) -> "WorkflowActionType":  # noqa ARG003
        """Set default member on unknown value."""
        return WorkflowActionType.UNKNOWN


# workflows
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
