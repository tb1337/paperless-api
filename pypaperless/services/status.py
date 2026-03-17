"""Provide `Status` service."""

from pypaperless.const import API_PATH, PaperlessResource
from pypaperless.models.status import Status

from .base import ServiceBase


class StatusService(ServiceBase):
    """Represent a factory for the Paperless `Status` model."""

    _api_path = API_PATH["status"]
    _resource = PaperlessResource.STATUS

    _resource_cls = Status

    async def __call__(self) -> Status:
        """Request the `Status` model data."""
        res = await self._client.request_json("get", self._api_path)
        return self._resource_cls.from_data(self._client, res)
