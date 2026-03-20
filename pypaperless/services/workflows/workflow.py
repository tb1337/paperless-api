"""Provide `Workflow` related services."""

from typing import TYPE_CHECKING

from pypaperless.const import API_PATH, PaperlessResource
from pypaperless.models.workflows.workflow import Workflow
from pypaperless.services import mixins
from pypaperless.services.base import ResourceService

from .actions import WorkflowActionService
from .triggers import WorkflowTriggerService

if TYPE_CHECKING:
    from pypaperless import Paperless


class WorkflowService(
    ResourceService,
    mixins.CallableService[Workflow],
    mixins.IterableService[Workflow],
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
        """Return the ``WorkflowActionService`` sub-service.

        Example::

            action = await paperless.workflows.actions(5)

        """
        return self._actions

    @property
    def triggers(self) -> WorkflowTriggerService:
        """Return the ``WorkflowTriggerService`` sub-service.

        Example::

            trigger = await paperless.workflows.triggers(23)

        """
        return self._triggers
