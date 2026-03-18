"""Provide `Workflow` related models."""

from typing import Any, ClassVar

from pypaperless.const import API_PATH
from pypaperless.models.base import PaperlessModel


class Workflow(PaperlessModel):
    """Represent a Paperless `Workflow`."""

    _api_path: ClassVar[str] = API_PATH["workflows_single"]

    id: int | None = None
    name: str | None = None
    order: int | None = None
    enabled: bool | None = None
    actions: list[Any] | None = None
    triggers: list[Any] | None = None
