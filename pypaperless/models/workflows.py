"""Provide `Workflow` related models."""

from typing import Any, ClassVar

from pypaperless.const import API_PATH

from . import mixins
from .base import PaperlessModel
from .common import (
    WorkflowActionEmailType,
    WorkflowActionType,
    WorkflowActionWebhookType,
    WorkflowTriggerScheduleDateFieldType,
    WorkflowTriggerSourceType,
    WorkflowTriggerType,
)


class WorkflowAction(PaperlessModel):
    """Represent a Paperless `WorkflowAction`."""

    _api_path: ClassVar[str] = API_PATH["workflow_actions_single"]

    id: int | None = None
    type: WorkflowActionType | None = None
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
    assign_custom_fields_values: dict[str, Any] | None = None
    remove_all_tags: bool | None = None
    remove_tags: list[int] | None = None
    remove_all_correspondents: bool | None = None
    remove_correspondents: list[int] | None = None
    remove_all_document_types: bool | None = None
    remove_document_types: list[int] | None = None
    remove_all_storage_paths: bool | None = None
    remove_storage_paths: list[int] | None = None
    remove_custom_fields: list[int] | None = None
    remove_all_custom_fields: bool | None = None
    remove_all_owners: bool | None = None
    remove_owners: list[int] | None = None
    remove_all_permissions: bool | None = None
    remove_view_users: list[int] | None = None
    remove_view_groups: list[int] | None = None
    remove_change_users: list[int] | None = None
    remove_change_groups: list[int] | None = None
    email: WorkflowActionEmailType | None = None
    webhook: WorkflowActionWebhookType | None = None


class WorkflowTrigger(PaperlessModel, mixins.MatchingFieldsMixin):
    """Represent a Paperless `WorkflowTrigger`."""

    _api_path: ClassVar[str] = API_PATH["workflow_triggers_single"]

    id: int | None = None
    sources: list[WorkflowTriggerSourceType] | None = None
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
    schedule_date_field: WorkflowTriggerScheduleDateFieldType | None = None
    schedule_date_custom_field: int | None = None


class Workflow(PaperlessModel):
    """Represent a Paperless `Workflow`."""

    _api_path: ClassVar[str] = API_PATH["workflows_single"]

    id: int | None = None
    name: str | None = None
    order: int | None = None
    enabled: bool | None = None
    actions: list[Any] | None = None
    triggers: list[Any] | None = None
