"""Provide `RemoteVersion` service."""

from pypaperless.const import API_PATH, PaperlessResource
from pypaperless.models.remote_version import RemoteVersion

from .base import ResourceService


class RemoteVersionService(ResourceService):
    """Represent a factory for Paperless `Remote Version` models."""

    _api_path = API_PATH["remote_version"]
    _resource = PaperlessResource.REMOTE_VERSION

    _resource_cls = RemoteVersion

    async def __call__(self) -> RemoteVersion:
        """Request the `Remote Version` model data."""
        res = await self._client.request_json("get", self._api_path)
        return self._resource_cls.from_data(self._client, res)
