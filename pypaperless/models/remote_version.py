"""Provide `Remote Version` related models."""

from typing import ClassVar

from pypaperless.const import API_PATH

from .base import PaperlessModel


class RemoteVersion(PaperlessModel):
    """Represent Paperless `Remote Version`."""

    _api_path: ClassVar[str] = API_PATH["remote_version"]

    version: str | None = None
    update_available: bool | None = None
