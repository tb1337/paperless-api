"""Provide `WorkflowAction` related services."""

from pypaperless.const import API_PATH, PaperlessResource
from pypaperless.models.workflows.actions import WorkflowAction
from pypaperless.services import mixins
from pypaperless.services.base import ResourceService


class WorkflowActionService(
    ResourceService,
    mixins.CallableMixin[WorkflowAction],
    mixins.IterableMixin[WorkflowAction],
):
    """Represent a factory for Paperless `WorkflowAction` models."""

    _api_path = API_PATH["workflow_actions"]
    _resource = PaperlessResource.WORKFLOW_ACTIONS

    _resource_cls = WorkflowAction
