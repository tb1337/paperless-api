"""Provide `WorkflowTrigger` related services."""

from pypaperless.const import EndpointPath
from pypaperless.models.workflows.triggers import WorkflowTrigger
from pypaperless.services import mixins
from pypaperless.services.base import ResourceService


class WorkflowTriggerService(
    ResourceService,
    mixins.CallableService[WorkflowTrigger],
    mixins.IterableService[WorkflowTrigger],
):
    """Represent a factory for Paperless `WorkflowTrigger` models."""

    _api_path = EndpointPath.WORKFLOW_TRIGGERS

    _resource_cls = WorkflowTrigger
