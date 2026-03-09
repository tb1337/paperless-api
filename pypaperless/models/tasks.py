"""Provide `Task` related models and services."""

import datetime
from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, Any, ClassVar

from pypaperless.const import API_PATH, PaperlessResource
from pypaperless.exceptions import TaskNotFoundError

from .base import ServiceBase, PaperlessModel
from .common import TaskStatusType, TaskType

if TYPE_CHECKING:
    from pypaperless import Paperless


class Task(PaperlessModel):
    """Represent a Paperless `Task`."""

    _api_path: ClassVar[str] = API_PATH["tasks_single"]

    id: int | None = None
    task_id: str | None = None
    task_name: str | None = None
    task_file_name: str | None = None
    date_created: datetime.datetime | None = None
    date_done: datetime.datetime | None = None
    type: TaskType | None = None
    status: TaskStatusType | None = None
    result: str | None = None
    acknowledged: bool | None = None
    related_document: int | None = None
    owner: int | None = None

    def __init__(self, client: "Paperless", data: dict[str, Any], **kwargs: Any) -> None:
        """Initialize a `Task` instance."""
        super().__init__(client, data, **kwargs)
        self._format_api_path(data)


class TaskService(ServiceBase):
    """Represent a factory for Paperless `Task` models."""

    _api_path = API_PATH["tasks"]
    _resource = PaperlessResource.TASKS

    _resource_cls = Task

    async def __aiter__(self) -> AsyncIterator[Task]:
        """Iterate over task items.

        Example:
        -------
        ```python
        async for task in paperless.tasks:
            # do something
        ```

        """
        res = await self._client.request_json("get", self._api_path)
        for data in res:
            yield self._resource_cls.create_with_data(self._client, data, fetched=True)

    async def __call__(self, task_id: int | str) -> Task:
        """Request exactly one task by id.

        If task_id is `str`: interpret it as a task uuid.
        If task_id is `int`: interpret it as a primary key.

        Example:
        -------
        ```python
        task = await paperless.tasks("uuid-string")
        task = await paperless.tasks(1337)
        ```

        """
        if isinstance(task_id, str):
            params = {
                "task_id": task_id,
            }
            res = await self._client.request_json("get", self._api_path, params=params)
            try:
                item = self._resource_cls.create_with_data(self._client, res.pop(), fetched=True)
            except IndexError as exc:
                raise TaskNotFoundError(task_id) from exc
        else:
            data = {
                "id": task_id,
            }
            item = self._resource_cls.create_with_data(self._client, data)
            await item.load()

        return item
