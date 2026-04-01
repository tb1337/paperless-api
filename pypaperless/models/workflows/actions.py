"""Provide `WorkflowAction` related models."""

from enum import Enum
from typing import Any, ClassVar, Self

from pydantic import BaseModel

from pypaperless.const import EndpointPath
from pypaperless.models.base import PaperlessModel


class WorkflowActionType(Enum):
    """Represent a subtype of `Workflow`."""

    ASSIGNMENT = 1
    REMOVAL = 2
    EMAIL = 3
    WEBHOOK = 4
    UNKNOWN = -1

    @classmethod
    def _missing_(cls, *_: object) -> Self:
        """Return the UNKNOWN member for any unrecognised value."""
        return cls["UNKNOWN"]


class WorkflowActionEmail(BaseModel):
    """Represent a subtype of `WorkflowAction`."""

    id: int | None = None
    to: str | None = None
    subject: str | None = None
    body: str | None = None
    include_document: bool | None = None


class WorkflowActionWebhook(BaseModel):
    """Represent a subtype of `WorkflowAction`."""

    id: int | None = None
    url: str | None = None
    use_params: bool | None = None
    as_json: bool | None = None
    params: dict[str, Any] | None = None
    body: str | None = None
    headers: dict[str, str] | None = None
    include_document: bool | None = None


class WorkflowAction(PaperlessModel):
    """Represent a Paperless `WorkflowAction`."""

    _api_path: ClassVar[str] = EndpointPath.WORKFLOW_ACTIONS_SINGLE

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
    email: WorkflowActionEmail | None = None
    webhook: WorkflowActionWebhook | None = None
