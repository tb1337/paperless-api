"""Provide `Workflow` related services."""

from typing import TYPE_CHECKING

from pypaperless.const import API_PATH, PaperlessResource
from pypaperless.models.workflows import Workflow, WorkflowAction, WorkflowTrigger

from . import mixins
from .base import ServiceBase

if TYPE_CHECKING:
    from pypaperless import Paperless


class WorkflowActionService(
    ServiceBase,
    mixins.CallableMixin[WorkflowAction],
    mixins.IterableMixin[WorkflowAction],
):
    """Represent a factory for Paperless `WorkflowAction` models."""

    _api_path = API_PATH["workflow_actions"]
    _resource = PaperlessResource.WORKFLOW_ACTIONS

    _resource_cls = WorkflowAction


class WorkflowTriggerService(
    ServiceBase,
    mixins.CallableMixin[WorkflowTrigger],
    mixins.IterableMixin[WorkflowTrigger],
):
    """Represent a factory for Paperless `WorkflowTrigger` models."""

    _api_path = API_PATH["workflow_triggers"]
    _resource = PaperlessResource.WORKFLOW_TRIGGERS

    _resource_cls = WorkflowTrigger


class WorkflowService(
    ServiceBase,
    mixins.CallableMixin[Workflow],
    mixins.IterableMixin[Workflow],
):
    """Represent a factory for Paperless `Workflow` models."""

    _api_path = API_PATH["workflows"]
    _resource = PaperlessResource.WORKFLOWS

    _resource_cls = Workflow

    def __init__(self, client: "Paperless") -> None:
        """Initialize a `WorkflowService` instance."""
        super().__init__(client)

        self._actions = WorkflowActionService(client)
        self._triggers = WorkflowTriggerService(client)

    @property
    def actions(self) -> WorkflowActionService:
        """Return the attached `WorkflowActionService` instance.

        Example:
        -------
        ```python
        wf_action = await paperless.workflows.actions(5)
        ```

        """
        return self._actions

    @property
    def triggers(self) -> WorkflowTriggerService:
        """Return the attached `WorkflowTriggerService` instance.

        Example:
        -------
        ```python
        wf_trigger = await paperless.workflows.triggers(23)
        ```

        """
        return self._triggers
