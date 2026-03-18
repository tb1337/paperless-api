"""Provide `WorkflowTrigger` related services."""

from pypaperless.const import API_PATH, PaperlessResource
from pypaperless.models.workflows.triggers import WorkflowTrigger
from pypaperless.services import mixins
from pypaperless.services.base import ServiceBase


class WorkflowTriggerService(
    ServiceBase,
    mixins.CallableMixin[WorkflowTrigger],
    mixins.IterableMixin[WorkflowTrigger],
):
    """Represent a factory for Paperless `WorkflowTrigger` models."""

    _api_path = API_PATH["workflow_triggers"]
    _resource = PaperlessResource.WORKFLOW_TRIGGERS

    _resource_cls = WorkflowTrigger
