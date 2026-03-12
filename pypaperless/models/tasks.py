"""Provide `Task` related models."""

import datetime
from enum import Enum
from typing import ClassVar

from pypaperless.const import API_PATH

from .base import PaperlessModel


class TaskType(Enum):
    """Represent a subtype of `Task`."""

    AUTO = "auto_task"
    SCHEDULED = "scheduled_task"
    MANUAL = "manual_task"
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls: type, *_: object) -> "TaskType":
        """Set default member on unknown value."""
        return TaskType.UNKNOWN


class TaskStatus(Enum):
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
    def _missing_(cls: type, *_: object) -> "TaskStatus":
        """Set default member on unknown value."""
        return TaskStatus.UNKNOWN


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
