"""Provide `Task` service."""

from collections.abc import AsyncIterator
from typing import Unpack, cast

from pypaperless.const import API_PATH, PaperlessResource
from pypaperless.exceptions import TaskNotFoundError
from pypaperless.models.filters import TaskFilters
from pypaperless.models.tasks import Task

from .base import ResourceService


class TaskService(ResourceService):
    """Represent a factory for Paperless `Task` models."""

    _api_path = API_PATH["tasks"]
    _resource = PaperlessResource.TASKS

    _resource_cls = Task

    async def __aiter__(self) -> AsyncIterator[Task]:
        """Iterate over all task items.

        Example::

            async for task in paperless.tasks:
                print(task.task_id, task.status)

        """
        async for item in self.filter():
            yield item

    async def filter(self, **kwargs: Unpack[TaskFilters]) -> AsyncIterator[Task]:
        """Iterate over task items with optional server-side filters.

        See :class:`~pypaperless.models.filters.TaskFilters` for available keys.
        When called with no arguments, returns all tasks (same as iterating directly).

        Example::

            async for task in paperless.tasks.filter(status="SUCCESS", acknowledged=False):
                print(task.task_id)

        """
        res = await self._runtime.transport.get(self._api_path, params=dict(kwargs))
        for data in res:
            yield self._resource_cls.from_data(self._runtime, data)

    async def __call__(self, task_id: int | str) -> Task:
        """Fetch a single task by primary key or Celery UUID.

        Args:
            task_id: An ``int`` primary key, or a ``str`` Celery task UUID.

        Example::

            task = await paperless.tasks("a1b2c3d4-...")
            task = await paperless.tasks(1337)

        """
        if isinstance(task_id, str):
            params = {
                "task_id": task_id,
            }
            res = await self._runtime.transport.get(self._api_path, params=params)
            try:
                return self._resource_cls.from_data(self._runtime, res.pop())
            except IndexError as exc:
                raise TaskNotFoundError(task_id) from exc
        else:
            api_path = self._resource_cls.format_api_path(pk=task_id)
            data = await self._runtime.transport.get(api_path)
            return self._resource_cls.from_data(self._runtime, data)

    async def acknowledge(self, tasks: list[int]) -> int:
        """Acknowledge a list of tasks by primary key.

        Returns the number of tasks that were acknowledged.

        Args:
            tasks: List of task primary keys to acknowledge.

        Example::

            count = await paperless.tasks.acknowledge([1, 2, 3])

        """
        data = cast(
            "dict[str, object]",
            await self._runtime.transport.post(
                API_PATH["tasks_acknowledge"],
                json={"tasks": tasks},
            ),
        )
        return cast("int", data["result"])

    async def run(self, task_id: str) -> Task:
        """Trigger a task by Celery UUID and return the resulting ``Task``.

        Args:
            task_id: Celery task UUID string.

        Example::

            task = await paperless.tasks.run("a1b2c3d4-...")

        """
        data = cast(
            "dict[str, object]",
            await self._runtime.transport.post(
                API_PATH["tasks_run"],
                json={"task_id": task_id},
            ),
        )
        return self._resource_cls.from_data(self._runtime, data)
