"""Provide `Task` service."""

from collections.abc import AsyncIterator
from typing import Unpack

from pypaperless.const import API_PATH, PaperlessResource
from pypaperless.exceptions import TaskNotFoundError
from pypaperless.models.filters import TaskFilters
from pypaperless.models.tasks import Task

from .base import ServiceBase


class TaskService(ServiceBase):
    """Represent a factory for Paperless `Task` models."""

    _api_path = API_PATH["tasks"]
    _resource = PaperlessResource.TASKS

    _resource_cls = Task

    async def __aiter__(self) -> AsyncIterator[Task]:
        """Iterate over all task items.

        Example:
        -------
        ```python
        async for task in paperless.tasks:
            # do something
        ```

        """
        async for item in self.filter():
            yield item

    async def filter(self, **kwargs: Unpack[TaskFilters]) -> AsyncIterator[Task]:
        """Iterate over task items with optional server-side filters.

        See :class:`~pypaperless.models.filters.TaskFilters` for available keys.
        When called with no arguments, returns all tasks (same as iterating directly).

        Example:
        -------
        ```python
        async for task in paperless.tasks.filter(status="SUCCESS", acknowledged=False):
            # do something
        ```

        """
        res = await self._client.request_json("get", self._api_path, params=dict(kwargs))
        for data in res:
            yield self._resource_cls.create_with_data(self._client, data)

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
                return self._resource_cls.create_with_data(self._client, res.pop())
            except IndexError as exc:
                raise TaskNotFoundError(task_id) from exc
        else:
            api_path = self._resource_cls.format_api_path(pk=task_id)
            data = await self._client.request_json("get", api_path)
            return self._resource_cls.create_with_data(self._client, data)
