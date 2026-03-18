"""Provide `Group` related models."""

from typing import ClassVar

from pypaperless.const import API_PATH
from pypaperless.models.base import PaperlessModel


class Group(PaperlessModel):
    """Represent a Paperless `Group`."""

    _api_path: ClassVar[str] = API_PATH["groups_single"]

    id: int
    name: str | None = None
    permissions: list[str] | None = None
