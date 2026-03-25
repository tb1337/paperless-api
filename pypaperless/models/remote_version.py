"""Provide `Remote Version` related models."""

from typing import ClassVar

from pypaperless.const import EndpointPath

from .base import PaperlessModel


class RemoteVersion(PaperlessModel):
    """Represent Paperless `Remote Version`."""

    _api_path: ClassVar[str] = EndpointPath.REMOTE_VERSION

    version: str | None = None
    update_available: bool | None = None
