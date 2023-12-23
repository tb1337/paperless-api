"""Shared models."""

from enum import Enum, StrEnum


class ResourceType(StrEnum):
    """Types of api endpoints."""

    CONSUMPTION_TEMPLATES = "consumption_templates"
    CORRESPONDENTS = "correspondents"
    CUSTOM_FIELDS = "custom_fields"
    DOCUMENT_TYPES = "document_types"
    DOCUMENTS = "documents"
    GROUPS = "groups"
    MAIL_ACCOUNTS = "mail_accounts"
    MAIL_RULES = "mail_rules"
    SAVED_VIEWS = "saved_views"
    SHARE_LINKS = "share_links"
    STORAGE_PATHS = "storage_paths"
    TAGS = "tags"
    TASKS = "tasks"
    USERS = "users"
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls: type, value: object) -> "ResourceType":  # noqa ARG003
        """Set default member on unknown value."""
        return ResourceType.UNKNOWN


class MatchingAlgorithm(Enum):
    """Enum with matching algorithms."""

    NONE = 0
    ANY = 1
    ALL = 2
    LITERAL = 3
    REGEX = 4
    FUZZY = 5
    AUTO = 6
    UNKNOWN = -1

    @classmethod
    def _missing_(cls: type, value: object) -> "MatchingAlgorithm":  # noqa ARG003
        """Set default member on unknown value."""
        return MatchingAlgorithm.UNKNOWN


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


class FileVersion(Enum):
    """Enum with file version."""

    ARCHIVE = "archive"
    ORIGINAL = "original"
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls: type, value: object) -> "FileVersion":  # noqa ARG003
        """Set default member on unknown value."""
        return FileVersion.UNKNOWN


class TaskStatus(Enum):
    """Enum with task states."""

    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def _missing_(cls: type, value: object) -> "TaskStatus":  # noqa ARG003
        """Set default member on unknown value."""
        return TaskStatus.UNKNOWN


class ConsumptionTemplateSource(Enum):
    """Enum with consumption template sources."""

    FOLDER = 1
    API = 2
    EMAIL = 3
    UNKNOWN = -1

    @classmethod
    def _missing_(cls: type, value: object) -> "ConsumptionTemplateSource":  # noqa ARG003
        """Set default member on unknown value."""
        return ConsumptionTemplateSource.UNKNOWN
