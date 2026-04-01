"""Provide `WorkflowAction` related services."""

from pypaperless.const import EndpointPath, PaperlessResource
from pypaperless.models.workflows.actions import WorkflowAction
from pypaperless.services import mixins
from pypaperless.services.base import ResourceService


class WorkflowActionService(
    ResourceService,
    mixins.CallableService[WorkflowAction],
    mixins.IterableService[WorkflowAction],
):
    """Represent a factory for Paperless `WorkflowAction` models."""

    _api_path = EndpointPath.WORKFLOW_ACTIONS
    _resource = PaperlessResource.WORKFLOW_ACTIONS

    _resource_cls = WorkflowAction
