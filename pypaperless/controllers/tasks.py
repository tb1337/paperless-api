"""Controller for Paperless tasks resource."""

from collections.abc import AsyncGenerator
from typing import Any

from pypaperless.models import Task
from pypaperless.util import dataclass_from_dict

from .base import BaseController


class TasksController(BaseController[Task]):
    """Represent Paperless tasks resource."""

    _resource = Task

    async def get(self, **kwargs: Any) -> list[Task]:
        """Request list of task items."""
        res = await self._paperless.request_json("get", self.path, params=kwargs)
        data: list[Task] = [dataclass_from_dict(self.resource, item) for item in res]
        return data

    async def iterate(
        self,
        **kwargs: Any,
    ) -> AsyncGenerator[Task, None]:
        """Iterate pages and yield every task item."""
        res: list[Task] = await self.get(**kwargs)
        for item in res:
            yield item

    async def one(self, idx: str) -> Task | None:
        """Request exactly one task item by pk."""
        params = {
            "task_id": idx,
        }
        res = await self._paperless.request_json("get", self.path, params=params)
        if len(res) > 0:
            data: Task = dataclass_from_dict(self.resource, res.pop())
            return data
        return None
