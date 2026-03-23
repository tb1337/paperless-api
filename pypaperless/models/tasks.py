"""Provide `Task` related models."""

import datetime
from enum import StrEnum
from typing import ClassVar, Self, cast

from pypaperless.const import API_PATH

from .base import PaperlessModel


class TaskType(StrEnum):
    """Represent a subtype of `Task`."""

    AUTO = "auto_task"
    SCHEDULED = "scheduled_task"
    MANUAL = "manual_task"
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls, *_: object) -> Self:
        """Return the UNKNOWN member for any unrecognised value."""
        return cls["UNKNOWN"]


class TaskStatus(StrEnum):
    """Represent a subtype of `Task`."""

    FAILURE = "FAILURE"
    PENDING = "PENDING"
    RECEIVED = "RECEIVED"
    RETRY = "RETRY"
    REVOKED = "REVOKED"
    STARTED = "STARTED"
    SUCCESS = "SUCCESS"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def _missing_(cls, *_: object) -> Self:
        """Return the UNKNOWN member for any unrecognised value."""
        return cls["UNKNOWN"]


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
    status: TaskStatus | None = None
    result: str | None = None
    acknowledged: bool | None = None
    related_document: int | None = None
    owner: int | None = None

    async def acknowledge(self) -> int:
        """Shortcut for ``paperless.tasks.acknowledge([self.id])``."""
        return cast("int", await self._client.tasks.acknowledge([cast("int", self.id)]))

    async def run(self) -> "Task":
        """Shortcut for ``paperless.tasks.run(self.task_id)``."""
        return cast("Task", await self._client.tasks.run(cast("str", self.task_id)))
