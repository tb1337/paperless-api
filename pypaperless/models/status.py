"""Provide `Status` related models."""

import datetime
from typing import ClassVar, cast

from pydantic import BaseModel, Field

from pypaperless.const import API_PATH
from pypaperless.models.mixins.data_fields import EnumWithMissingFallback

from .base import PaperlessModel


class StatusType(EnumWithMissingFallback):
    """Represent a subtype of `Status`."""

    OK = "OK"
    ERROR = "ERROR"
    WARNING = "WARNING"
    UNKNOWN = "UNKNOWN"


class StatusDatabaseMigration(BaseModel):
    """Represent a subtype of `StatusDatabase`."""

    latest_migration: str | None = None
    unapplied_migrations: list[str] = Field(default_factory=list)


class StatusDatabase(BaseModel):
    """Represent a subtype of `Status`."""

    type: str | None = None
    url: str | None = None
    status: StatusType | None = None
    error: str | None = None
    migration_status: StatusDatabaseMigration | None = None


class StatusStorage(BaseModel):
    """Represent a subtype of `Status`."""

    total: int | None = None
    available: int | None = None


class StatusTasks(BaseModel):
    """Represent a subtype of `Status`."""

    redis_url: str | None = None
    redis_status: StatusType | None = None
    redis_error: str | None = None
    celery_status: StatusType | None = None
    celery_url: str | None = None
    celery_error: str | None = None
    index_status: StatusType | None = None
    index_last_modified: datetime.datetime | None = None
    index_error: str | None = None
    classifier_status: StatusType | None = None
    classifier_last_trained: datetime.datetime | None = None
    classifier_error: str | None = None
    sanity_check_status: StatusType | None = None
    sanity_check_last_run: datetime.datetime | None = None
    sanity_check_error: str | None = None


class Status(PaperlessModel):
    """Represent a Paperless `Status`."""

    _api_path: ClassVar[str] = API_PATH["status"]

    pngx_version: str | None = None
    server_os: str | None = None
    install_type: str | None = None
    storage: StatusStorage | None = None
    database: StatusDatabase | None = None
    tasks: StatusTasks | None = None

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

        return StatusType.ERROR in statuses
