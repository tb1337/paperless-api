"""PyPaperless common types."""

import datetime
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
    def _missing_(cls: type, *_: object) -> "CustomFieldType":
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
    def _missing_(cls: type, *_: object) -> "MatchingAlgorithmType":
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
    def _missing_(cls: type, *_: object) -> "ShareLinkFileVersionType":
        """Set default member on unknown value."""
        return ShareLinkFileVersionType.UNKNOWN


# status
class StatusType(Enum):
    """Represent a subtype of `Status`."""

    OK = "OK"
    ERROR = "ERROR"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def _missing_(cls: type, *_: object) -> "StatusType":
        """Set default member on unknown value."""
        return StatusType.UNKNOWN


# status
@dataclass(kw_only=True)
class StatusDatabaseMigrationStatusType:
    """Represent a subtype of `StatusDatabaseType`."""

    latest_migration: str | None = None
    unapplied_migrations: list[str] = field(default_factory=list)


# status
@dataclass(kw_only=True)
class StatusDatabaseType:
    """Represent a subtype of `Status`."""

    type: str | None = None
    url: str | None = None
    status: StatusType | None = None
    error: str | None = None
    migration_status: StatusDatabaseMigrationStatusType | None = None


# status
@dataclass(kw_only=True)
class StatusStorageType:
    """Represent a subtype of `Status`."""

    total: int | None = None
    available: int | None = None


# status
@dataclass(kw_only=True)
class StatusTasksType:
    """Represent a subtype of `Status`."""

    redis_url: str | None = None
    redis_status: StatusType | None = None
    redis_error: str | None = None
    celery_status: StatusType | None = None
    index_status: StatusType | None = None
    index_last_modified: datetime.datetime | None = None
    index_error: str | None = None
    classifier_status: StatusType | None = None
    classifier_last_trained: datetime.datetime | None = None
    classifier_error: str | None = None


# tasks
class TaskStatusType(Enum):
    """Represent a subtype of `Task`."""

    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def _missing_(cls: type, *_: object) -> "TaskStatusType":
        """Set default member on unknown value."""
        return TaskStatusType.UNKNOWN


# workflows
class WorkflowActionType(Enum):
    """Represent a subtype of `Workflow`."""

    ASSIGNMENT = 1
    UNKNOWN = -1

    @classmethod
    def _missing_(cls: type, *_: object) -> "WorkflowActionType":
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
    def _missing_(cls: type, *_: object) -> "WorkflowTriggerType":
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
    def _missing_(cls: type, *_: object) -> "WorkflowTriggerSourceType":
        """Set default member on unknown value."""
        return WorkflowTriggerSourceType.UNKNOWN
