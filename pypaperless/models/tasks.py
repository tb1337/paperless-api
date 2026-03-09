"""Provide `Task` related models."""

import datetime
from typing import TYPE_CHECKING, Any, ClassVar

from pypaperless.const import API_PATH

from .base import PaperlessModel
from .common import TaskStatusType, TaskType

if TYPE_CHECKING:
    from pypaperless import Paperless


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
    status: TaskStatusType | None = None
    result: str | None = None
    acknowledged: bool | None = None
    related_document: int | None = None
    owner: int | None = None

    def __init__(self, client: "Paperless", data: dict[str, Any], **kwargs: Any) -> None:
        """Initialize a `Task` instance."""
        super().__init__(client, data, **kwargs)
        self._format_api_path(data)
