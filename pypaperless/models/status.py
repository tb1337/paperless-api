"""Provide `Status` related models and helpers."""

from dataclasses import dataclass
from typing import cast

from pypaperless.const import API_PATH, PaperlessResource
from pypaperless.models.common import (
    StatusDatabaseType,
    StatusStorageType,
    StatusTasksType,
    StatusType,
)

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

    @property
    def has_errors(self) -> bool:
        """Return whether any status flag is `ERROR`."""
        statuses: list[StatusType] = [
            self.database.status if self.database and self.database.status else StatusType.OK,
            *[
                cast("StatusType", getattr(self.tasks, status, StatusType.OK))
                for status in (
                    "redis_status",
                    "celery_status",
                    "classifier_status",
                )
                if self.tasks
            ],
        ]

        return any(st == StatusType.ERROR for st in statuses)


class StatusHelper(HelperBase[Status]):
    """Represent a factory for the Paperless `Status` model."""

    _api_path = API_PATH["status"]
    _resource = PaperlessResource.STATUS
    _resource_public = False

    _resource_cls = Status

    async def __call__(self) -> Status:
        """Request the `Status` model data."""
        res = await self._api.request_json("get", self._api_path)
        return self._resource_cls.create_with_data(self._api, res, fetched=True)
