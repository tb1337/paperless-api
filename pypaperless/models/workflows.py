"""Model for workflow resource."""

from dataclasses import dataclass
from enum import Enum

from .base import PaperlessModel
from .matching import PaperlessModelMatchingMixin


class WorkflowTriggerType(Enum):
    """Enum with workflow trigger types."""

    CONSUMPTION = 1
    DOCUMENT_ADDED = 2
    DOCUMENT_UPDATED = 3
    UNKNOWN = -1

    @classmethod
    def _missing_(cls: type, value: object) -> "WorkflowTriggerType":  # noqa ARG003
        """Set default member on unknown value."""
        return WorkflowTriggerType.UNKNOWN


class WorkflowActionType(Enum):
    """Enum with workflow action types."""

    ASSIGNMENT = 1
    UNKNOWN = -1

    @classmethod
    def _missing_(cls: type, value: object) -> "WorkflowActionType":  # noqa ARG003
        """Set default member on unknown value."""
        return WorkflowActionType.UNKNOWN


class WorkflowTriggerSource(Enum):
    """Enum with workflow trigger sources."""

    CONSUME_FOLDER = 1
    API_UPLOAD = 2
    MAIL_FETCH = 3
    UNKNOWN = -1

    @classmethod
    def _missing_(cls: type, value: object) -> "WorkflowTriggerSource":  # noqa ARG003
        """Set default member on unknown value."""
        return WorkflowTriggerSource.UNKNOWN


@dataclass(kw_only=True)
class WorkflowTrigger(
    PaperlessModel,
    PaperlessModelMatchingMixin,
):  # pylint: disable=too-many-instance-attributes
    """Represent a workflow trigger on the Paperless api."""

    id: int | None = None
    sources: list[WorkflowTriggerSource] | None = None
    type: WorkflowTriggerType | None = None
    filter_path: str | None = None
    filter_filename: str | None = None
    filter_mailrule: int | None = None
    filter_has_tags: list[int] | None = None
    filter_has_correspondent: int | None = None
    filter_has_document_type: int | None = None


@dataclass(kw_only=True)
class WorkflowAction(PaperlessModel):  # pylint: disable=too-many-instance-attributes
    """Represent a workflow action on the Paperless api."""

    id: int | None = None
    type: WorkflowActionType | None = None
    assign_title: str | None = None
    assign_tags: list[int] | None = None
    assign_correspondent: int | None = None
    assign_document_type: int | None = None
    assign_storage_path: int | None = None
    assign_view_users: list[int] | None = None
    assign_view_groups: list[int] | None = None
    assign_change_users: list[int] | None = None
    assign_change_groups: list[int] | None = None
    assign_custom_fields: list[int] | None = None


@dataclass(kw_only=True)
class Workflow(PaperlessModel):  # pylint: disable=too-many-instance-attributes
    """Represent a workflow resource on the Paperless api."""

    id: int | None = None
    name: str | None = None
    order: int | None = None
    enabled: bool | None = None
    triggers: list[WorkflowTrigger] | None = None
    actions: list[WorkflowAction] | None = None


# old consumption templates model


class ConsumptionTemplateSource(Enum):
    """Enum with consumption template sources."""

    FOLDER = 1
    API = 2
    EMAIL = 3


@dataclass(kw_only=True)
class ConsumptionTemplate(PaperlessModel):  # pylint: disable=too-many-instance-attributes
    """Represent a consumption template resource on the Paperless api."""

    id: int | None = None
    name: str | None = None
    order: int | None = None
    sources: list[ConsumptionTemplateSource] | None = None
    filter_path: str | None = None
    filter_filename: str | None = None
    filter_mailrule: int | None = None
    assign_title: str | None = None
    assign_tags: list[int] | None = None
    assign_correspondent: int | None = None
    assign_document_type: int | None = None
    assign_storage_path: int | None = None
    assign_owner: int | None = None
    assign_view_users: list[int] | None = None
    assign_view_groups: list[int] | None = None
    assign_change_users: list[int] | None = None
    assign_change_groups: list[int] | None = None
    assign_custom_fields: list[int] | None = None
