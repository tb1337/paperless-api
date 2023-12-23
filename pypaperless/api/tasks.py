"""Customized endpoint for Paperless tasks."""

from collections.abc import AsyncGenerator
from typing import Any

from pypaperless.models import Task
from pypaperless.models.shared import ResourceType
from pypaperless.util import dataclass_from_dict

from .base import BaseEndpoint


class TasksEndpoint(BaseEndpoint[type[Task]]):
    """Represent Paperless tasks."""

    endpoint_cls = Task
    endpoint_type = ResourceType.TASKS

    async def get(self, **kwargs: Any) -> list[type[Task]]:  # type: ignore[override]
        """Request entities."""
        res: list[Any] = list(
            await self._paperless.request_json("get", self.endpoint, params=kwargs)
        )
        data: list[type[Task]] = [dataclass_from_dict(self.endpoint_cls, item) for item in res]
        return data

    async def iterate(
        self,
        **kwargs: Any,
    ) -> AsyncGenerator[type[Task], None]:
        """Iterate pages and yield every entity."""
        res: list[type[Task]] = await self.get(**kwargs)
        for item in res:
            yield item

    async def one(self, idx: Any) -> Task:  # type: ignore[override]
        """Request exactly one entity by id."""
        params = {
            "task_id": idx,
        }
        res = await self._paperless.request_json("get", self.endpoint, params=params)
        data: Task = dataclass_from_dict(self.endpoint_cls, res.pop())
        return data
