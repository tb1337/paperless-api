"""PyPaperless common types."""

import contextlib
import datetime
from dataclasses import dataclass, field
from enum import Enum, StrEnum
from typing import TYPE_CHECKING, Any, TypedDict

if TYPE_CHECKING:
    from pypaperless import Paperless

    from .classifiers import Correspondent, DocumentType, StoragePath, Tag
    from .custom_fields import CustomField


# custom_fields
class CustomFieldExtraDataSelectOptions(TypedDict):
    """Represent the `extra_data.select_options` field of a `CustomField`."""

    id: str | None
    label: str | None


class CustomFieldExtraData(TypedDict):
    """Represent the `extra_data` field of a `CustomField`."""

    default_currency: str | None
    select_options: list[CustomFieldExtraDataSelectOptions | None]


class CustomFieldType(Enum):
    """Represent a subtype of `CustomField`."""

    STRING = "string"
    URL = "url"
    DATE = "date"
    BOOLEAN = "boolean"
    INTEGER = "integer"
    FLOAT = "float"
    MONETARY = "monetary"
    DOCUMENT_LINK = "documentlink"
    SELECT = "select"
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls: type, *_: object) -> "CustomFieldType":
        """Set default member on unknown value."""
        return CustomFieldType.UNKNOWN


# documents
@dataclass(kw_only=True)
class CustomFieldValue:
    """Represent a subtype of `CustomField`."""

    field: int | None = None
    value: Any | None = None
    name: str | None = None
    data_type: CustomFieldType | None = None
    extra_data: CustomFieldExtraData | None = None


@dataclass(kw_only=True)
class CustomFieldBooleanValue(CustomFieldValue):
    """Represent a boolean `CustomFieldValue`."""

    value: bool | None = None


@dataclass(kw_only=True)
class CustomFieldDateValue(CustomFieldValue):
    """Represent a date `CustomFieldValue`."""

    value: datetime.datetime | str | None = None

    def __post_init__(self) -> None:
        """Convert the value to a datetime."""
        if isinstance(self.value, str):
            with contextlib.suppress(ValueError):
                self.value = datetime.datetime.fromisoformat(self.value)


@dataclass(kw_only=True)
class CustomFieldDocumentLinkValue(CustomFieldValue):
    """Represent a document link `CustomFieldValue`."""

    value: list[int] | None = None


@dataclass(kw_only=True)
class CustomFieldFloatValue(CustomFieldValue):
    """Represent a float `CustomFieldValue`."""

    value: float | None = None


@dataclass(kw_only=True)
class CustomFieldIntegerValue(CustomFieldValue):
    """Represent an integer `CustomFieldValue`."""

    value: int | None = None


@dataclass(kw_only=True)
class CustomFieldSelectValue(CustomFieldValue):
    """Represent a select `CustomFieldValue`."""

    value: int | None = None

    @property
    def labels(self) -> list[CustomFieldExtraDataSelectOptions | None]:
        """Return the list of labels of the `CustomField`."""
        if not self.extra_data:
            return []
        return self.extra_data["select_options"]

    @property
    def label(self) -> str | None:
        """Return the label for `value` or fall back to `None`."""
        for opt in self.labels:
            if opt and opt["id"] == self.value:
                return opt["label"]
        return None


@dataclass(kw_only=True)
class CustomFieldStringValue(CustomFieldValue):
    """Represent a string `CustomFieldValue`."""

    value: str | None = None


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


# api
@dataclass(kw_only=True)
class MasterDataInstance:
    """Represent a `MasterDataInstance`."""

    api: "Paperless"
    is_initialized: bool = False

    correspondents: list["Correspondent"] = field(default_factory=list)
    custom_fields: list["CustomField"] = field(default_factory=list)
    document_types: list["DocumentType"] = field(default_factory=list)
    storage_paths: list["StoragePath"] = field(default_factory=list)
    tags: list["Tag"] = field(default_factory=list)


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


# api
@dataclass(kw_only=True)
class PaperlessCache:
    """Represent a Paperless cache object."""

    custom_fields: dict[int, "CustomField"] | None = None


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


# statistics
@dataclass(kw_only=True)
class StatisticDocumentFileTypeCount:
    """Represent a Paperless statistics file type count."""

    mime_type: str | None = None
    mime_type_count: int | None = None


# status
class StatusType(Enum):
    """Represent a subtype of `Status`."""

    OK = "OK"
    ERROR = "ERROR"
    WARNING = "WARNING"
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
    celery_url: str | None = None
    celery_error: str | None = None
    index_status: StatusType | None = None
    index_last_modified: datetime.datetime | None = None
    index_error: str | None = None
    classifier_status: StatusType | None = None
    classifier_last_trained: datetime.datetime | None = None
    classifier_error: str | None = None
    sanity_check_status: StatusType | None = None
    sanity_check_last_run: datetime.datetime | None = None
    sanity_check_error: str | None = None


# tasks
class TaskStatusType(Enum):
    """Represent a subtype of `Task`."""

    PENDING = "PENDING"
    STARTED = "STARTED"
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
