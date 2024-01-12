"""Model for task resource."""

from dataclasses import dataclass
from enum import Enum

from .base import PaperlessModel


class TaskStatus(Enum):
    """Enum with task states."""

    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def _missing_(cls: type, value: object) -> "TaskStatus":  # noqa ARG003
        """Set default member on unknown value."""
        return TaskStatus.UNKNOWN


@dataclass(kw_only=True)
class Task(PaperlessModel):  # pylint: disable=too-many-instance-attributes
    """Represent a task resource in the Paperless api."""

    id: int | None = None
    task_id: str | None = None
    task_file_name: str | None = None
    date_created: str | None = None
    date_done: str | None = None
    type: str | None = None
    status: TaskStatus | None = None
    result: str | None = None
    acknowledged: bool | None = None
    related_document: int | None = None
