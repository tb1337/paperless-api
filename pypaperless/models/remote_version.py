"""Provide `Remote Version` related models and helpers."""

from typing import ClassVar

from pypaperless.const import API_PATH, PaperlessResource

from .base import HelperBase, PaperlessModel


class RemoteVersion(PaperlessModel):
    """Represent Paperless `Remote Version`."""

    _api_path: ClassVar[str] = API_PATH["remote_version"]

    version: str | None = None
    update_available: bool | None = None


class RemoteVersionHelper(HelperBase):
    """Represent a factory for Paperless `Remote Version` models."""

    _api_path = API_PATH["remote_version"]
    _resource = PaperlessResource.REMOTE_VERSION

    _resource_cls = RemoteVersion

    async def __call__(self) -> RemoteVersion:
        """Request the `Remote Version` model data."""
        res = await self._api.request_json("get", self._api_path)
        return self._resource_cls.create_with_data(self._api, res, fetched=True)
