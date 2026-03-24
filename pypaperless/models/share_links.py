"""Provide `ShareLink` related models."""

import datetime
from enum import StrEnum
from typing import ClassVar, Self

from pypaperless.const import API_PATH, PaperlessResource

from . import mixins
from .base import PaperlessModel


class ShareLinkFileVersion(StrEnum):
    """Represent a subtype of `ShareLink`."""

    ARCHIVE = "archive"
    ORIGINAL = "original"
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls, *_: object) -> Self:
        """Return the UNKNOWN member for any unrecognised value."""
        return cls["UNKNOWN"]


class ShareLink(
    PaperlessModel,
):
    """Represent a Paperless `ShareLink`."""

    _api_path: ClassVar[str] = API_PATH["share_links_single"]
    _resource: ClassVar[PaperlessResource] = PaperlessResource.SHARE_LINKS

    id: int
    created: datetime.datetime | None = None
    expiration: datetime.datetime | None = None
    slug: str | None = None
    document: int | None = None
    file_version: ShareLinkFileVersion | None = None


class ShareLinkDraft(PaperlessModel, mixins.CreatableModel):
    """Represent a new Paperless `ShareLink`, which is not stored in Paperless."""

    _api_path: ClassVar[str] = API_PATH["share_links"]
    _resource: ClassVar[PaperlessResource] = PaperlessResource.SHARE_LINKS

    _create_required_fields: ClassVar[set[str]] = {"document", "file_version"}

    expiration: datetime.datetime | None = None
    document: int | None = None
    file_version: ShareLinkFileVersion | None = None
