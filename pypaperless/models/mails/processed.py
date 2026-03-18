"""Provide `ProcessedMail` related models."""

import datetime
from typing import ClassVar

from pypaperless.const import API_PATH
from pypaperless.models.base import PaperlessModel


class ProcessedMail(PaperlessModel):
    """Represent a Paperless `ProcessedMail`."""

    _api_path: ClassVar[str] = API_PATH["processed_mail_single"]

    id: int | None = None
    owner: int | None = None
    rule: int | None = None
    folder: str | None = None
    uid: str | None = None
    subject: str | None = None
    received: datetime.datetime | None = None
    processed: datetime.datetime | None = None
    status: str | None = None
    error: str | None = None
