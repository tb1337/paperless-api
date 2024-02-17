"""Provide `Workflow` related models and helpers."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from pypaperless.const import API_PATH, PaperlessResource

from .base import HelperBase, PaperlessModel
from .common import WorkflowActionType, WorkflowTriggerSourceType, WorkflowTriggerType
from .mixins import helpers, models

if TYPE_CHECKING:
    from pypaperless import Paperless


@dataclass(init=False)
class WorkflowAction(PaperlessModel):
    """Represent a Paperless `WorkflowAction`."""

    _api_path = API_PATH["workflow_actions_single"]

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

    def __init__(self, api: "Paperless", data: dict[str, Any]):
        """Initialize a `Workflow` instance."""
        super().__init__(api, data)

        self._api_path = self._api_path.format(pk=data.get("id"))


@dataclass(init=False)
class WorkflowTrigger(
    PaperlessModel,
    models.MatchingFieldsMixin,
):
    """Represent a Paperless `WorkflowTrigger`."""

    _api_path = API_PATH["workflow_triggers_single"]

    id: int | None = None
    sources: list[WorkflowTriggerSourceType] | None = None
    type: WorkflowTriggerType | None = None
    filter_path: str | None = None
    filter_filename: str | None = None
    filter_mailrule: int | None = None
    filter_has_tags: list[int] | None = None
    filter_has_correspondent: int | None = None
    filter_has_document_type: int | None = None

    def __init__(self, api: "Paperless", data: dict[str, Any]):
        """Initialize a `Workflow` instance."""
        super().__init__(api, data)

        self._api_path = self._api_path.format(pk=data.get("id"))


@dataclass(init=False)
class Workflow(PaperlessModel):
    """Represent a Paperless `Workflow`."""

    _api_path = API_PATH["workflows_single"]

    id: int | None = None
    name: str | None = None
    order: int | None = None
    enabled: bool | None = None
    actions: list[WorkflowAction] | None = None
    triggers: list[WorkflowTrigger] | None = None

    def __init__(self, api: "Paperless", data: dict[str, Any]):
        """Initialize a `Workflow` instance."""
        super().__init__(api, data)

        self._api_path = self._api_path.format(pk=data.get("id"))


class WorkflowActionHelper(
    HelperBase[WorkflowAction],
    helpers.CallableMixin[WorkflowAction],
    helpers.IterableMixin[WorkflowAction],
):
    """Represent a factory for Paperless `WorkflowAction` models."""

    _api_path = API_PATH["workflow_actions"]
    _resource = PaperlessResource.WORKFLOW_ACTIONS

    _resource_cls = WorkflowAction


class WorkflowTriggerHelper(
    HelperBase[WorkflowTrigger],
    helpers.CallableMixin[WorkflowTrigger],
    helpers.IterableMixin[WorkflowTrigger],
):
    """Represent a factory for Paperless `WorkflowTrigger` models."""

    _api_path = API_PATH["workflow_triggers"]
    _resource = PaperlessResource.WORKFLOW_TRIGGERS

    _resource_cls = WorkflowTrigger


class WorkflowHelper(
    HelperBase[Workflow],
    helpers.CallableMixin[Workflow],
    helpers.IterableMixin[Workflow],
):
    """Represent a factory for Paperless `Workflow` models."""

    _api_path = API_PATH["workflows"]
    _resource = PaperlessResource.WORKFLOWS

    _resource_cls = Workflow

    def __init__(self, api: "Paperless") -> None:
        """Initialize a `WorkflowHelper` instance."""
        super().__init__(api)

        self._actions = WorkflowActionHelper(api)
        self._triggers = WorkflowTriggerHelper(api)

    @property
    def actions(self) -> WorkflowActionHelper:
        """Return the attached `WorkflowActionHelper` instance.

        Example:
        ```python
        wf_action = await paperless.workflows.actions(5)
        ```
        """
        return self._actions

    @property
    def triggers(self) -> WorkflowTriggerHelper:
        """Return the attached `WorkflowTriggerHelper` instance.

        Example:
        ```python
        wf_trigger = await paperless.workflows.triggers(23)
        ```
        """
        return self._triggers
