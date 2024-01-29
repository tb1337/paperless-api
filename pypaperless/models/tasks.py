"""Provide `Task` related models and helpers."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, final

from pypaperless.const import API_PATH, PaperlessResource

from .base import HelperBase, PaperlessModel
from .common import TaskStatusType
from .mixins import models

if TYPE_CHECKING:
    from pypaperless import Paperless


@final
@dataclass(init=False)
class Task(  # pylint: disable=too-many-instance-attributes
    PaperlessModel,
    models.PermissionFieldsMixin,
):
    """Represent a Paperless `Task`."""

    _api_path = API_PATH["tasks"]

    id: int | None = None
    task_id: str | None = None
    task_file_name: str | None = None
    date_created: str | None = None
    date_done: str | None = None
    type: str | None = None
    status: TaskStatusType | None = None
    result: str | None = None
    acknowledged: bool | None = None
    related_document: int | None = None

    def __init__(self, api: "Paperless", data: dict[str, Any]):
        """Initialize a `Task` instance."""
        super().__init__(api, data)

        self._api_path = self._api_path.format(pk=data.get("id"))


@final
class TaskHelper(
    HelperBase[Task],
):
    """Represent a factory for Paperless `Task` models."""

    _api_path = API_PATH["tasks"]
    _resource = PaperlessResource.TASKS

    _resource_cls = Task

    async def __call__(self, task_id: str) -> Task:
        """Request exactly one task by task_id.

        Example:
        ```python
        task = await paperless.tasks("uuid-like-string")
        ```
        """
        params = {
            "task_id": task_id,
        }
        res = await self._api.request_json("get", self._api_path, params=params)
        item = self._resource_cls.create_with_data(self._api, res.pop(), fetched=True)
        return item
