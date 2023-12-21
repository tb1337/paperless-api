"""Model for task resource."""

from dataclasses import dataclass

from .base import PaperlessModel
from .shared import TaskStatus


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
