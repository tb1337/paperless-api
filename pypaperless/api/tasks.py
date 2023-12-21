"""Customized endpoint for Paperless tasks."""

from collections.abc import Generator
from typing import Any

from pypaperless.models import Task
from pypaperless.models.shared import ResourceType
from pypaperless.util import dataclass_from_dict

from .base import RT, BaseEndpoint


class TasksEndpoint(BaseEndpoint[type[Task]]):
    """Represent Paperless tasks."""

    endpoint_cls = Task
    endpoint_type = ResourceType.TASKS

    async def get(
        self,
        **kwargs: dict[str, Any],
    ) -> list[RT]:
        """Request entities."""
        res = await self._paperless.request_json("get", self.endpoint, params=kwargs)
        return [dataclass_from_dict(self.endpoint_cls, item) for item in res]

    async def iterate(
        self,
        **kwargs: dict[str, Any],
    ) -> Generator[Task, None, None]:
        """Iterate pages and yield every entity."""
        res = await self.get(**kwargs)
        for item in res:
            yield item

    async def one(self, idx: str) -> RT:
        """Request exactly one entity by id."""
        params = {
            "task_id": idx,
        }
        res = await self._paperless.request_json("get", self.endpoint, params=params)
        return dataclass_from_dict(self.endpoint_cls, res.pop())
