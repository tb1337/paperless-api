"""Model for task resource."""

import uuid
from dataclasses import dataclass

from .base import PaperlessModel
from .shared import TaskStatus


@dataclass(kw_only=True)
class Task(PaperlessModel):
    """Represent a task resource in the Paperless api."""

    id: int | None = None
    task_id: uuid.UUID | None = None
    task_file_name: str | None = None
    date_created: str | None = None
    date_done: str | None = None
    type: str | None = None
    status: TaskStatus | None = None
    result: str | None = None
    acknowledged: bool | None = None
    related_document: int | None = None
