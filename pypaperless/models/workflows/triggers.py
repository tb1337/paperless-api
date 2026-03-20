"""Provide `WorkflowTrigger` related models."""

from enum import Enum, StrEnum
from typing import ClassVar, Self

from pypaperless.const import API_PATH
from pypaperless.models import mixins
from pypaperless.models.base import PaperlessModel


class WorkflowTriggerType(Enum):
    """Represent a subtype of `Workflow`."""

    CONSUMPTION = 1
    DOCUMENT_ADDED = 2
    DOCUMENT_UPDATED = 3
    SCHEDULED = 4
    UNKNOWN = -1

    @classmethod
    def _missing_(cls, *_: object) -> Self:
        """Return the UNKNOWN member for any unrecognised value."""
        return cls["UNKNOWN"]


class WorkflowTriggerScheduleDateField(StrEnum):
    """Represent a subtype of `WorkflowTrigger`."""

    ADDED = "added"
    CREATED = "created"
    MODIFIED = "modified"
    CUSTOM_FIELD = "custom_field"
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls, *_: object) -> Self:
        """Return the UNKNOWN member for any unrecognised value."""
        return cls["UNKNOWN"]


class WorkflowTriggerSource(Enum):
    """Represent a subtype of `Workflow`."""

    CONSUME_FOLDER = 1
    API_UPLOAD = 2
    MAIL_FETCH = 3
    WEB_UI = 4
    UNKNOWN = -1

    @classmethod
    def _missing_(cls, *_: object) -> Self:
        """Return the UNKNOWN member for any unrecognised value."""
        return cls["UNKNOWN"]


class WorkflowTrigger(PaperlessModel, mixins.MatchingFieldsModel):
    """Represent a Paperless `WorkflowTrigger`."""

    _api_path: ClassVar[str] = API_PATH["workflow_triggers_single"]

    id: int | None = None
    sources: list[WorkflowTriggerSource] | None = None
    type: WorkflowTriggerType | None = None
    filter_path: str | None = None
    filter_filename: str | None = None
    filter_mailrule: int | None = None
    filter_has_tags: list[int] | None = None
    filter_has_all_tags: list[int] | None = None
    filter_has_not_tags: list[int] | None = None
    filter_custom_field_query: str | None = None
    filter_has_not_correspondents: list[int] | None = None
    filter_has_not_document_types: list[int] | None = None
    filter_has_not_storage_paths: list[int] | None = None
    filter_has_correspondent: int | None = None
    filter_has_document_type: int | None = None
    filter_has_storage_path: int | None = None
    schedule_offset_days: int | None = None
    schedule_is_recurring: bool | None = None
    schedule_recurring_interval_days: int | None = None
    schedule_date_field: WorkflowTriggerScheduleDateField | None = None
    schedule_date_custom_field: int | None = None
