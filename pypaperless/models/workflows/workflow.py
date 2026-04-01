"""Provide `Workflow` related models."""

from typing import Any, ClassVar

from pypaperless.const import EndpointPath
from pypaperless.models.base import PaperlessModel


class Workflow(PaperlessModel):
    """Represent a Paperless `Workflow`."""

    _api_path: ClassVar[str] = EndpointPath.WORKFLOWS_SINGLE

    id: int | None = None
    name: str | None = None
    order: int | None = None
    enabled: bool | None = None
    actions: list[Any] | None = None
    triggers: list[Any] | None = None
