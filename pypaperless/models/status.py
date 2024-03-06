"""Provide `Status` related models and helpers."""

from dataclasses import dataclass

from pypaperless.const import API_PATH, PaperlessResource
from pypaperless.models.common import StatusDatabaseType, StatusStorageType, StatusTasksType

from .base import HelperBase, PaperlessModel


@dataclass(init=False)
class Status(PaperlessModel):
    """Represent a Paperless `Status`."""

    _api_path = API_PATH["status"]

    pngx_version: str | None = None
    server_os: str | None = None
    install_type: str | None = None
    storage: StatusStorageType | None = None
    database: StatusDatabaseType | None = None
    tasks: StatusTasksType | None = None


class StatusHelper(HelperBase[Status]):
    """Represent a factory for the Paperless `Status` model."""

    _api_path = API_PATH["status"]
    _resource = PaperlessResource.STATUS

    _resource_cls = Status

    async def __call__(self) -> Status:
        """Request the `Status` model data."""
        res = await self._api.request_json("get", self._api_path)
        item = self._resource_cls.create_with_data(self._api, res, fetched=True)

        return item
