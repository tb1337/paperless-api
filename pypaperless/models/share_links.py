"""Provide `ShareLink` related models."""

import datetime
from enum import Enum
from typing import ClassVar

from pypaperless.const import API_PATH

from . import mixins
from .base import PaperlessModel


class ShareLinkFileVersion(Enum):
    """Represent a subtype of `ShareLink`."""

    ARCHIVE = "archive"
    ORIGINAL = "original"
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls: type, *_: object) -> "ShareLinkFileVersion":
        """Set default member on unknown value."""
        return ShareLinkFileVersion.UNKNOWN


class ShareLink(
    PaperlessModel,
):
    """Represent a Paperless `ShareLink`."""

    _api_path: ClassVar[str] = API_PATH["share_links_single"]

    id: int
    created: datetime.datetime | None = None
    expiration: datetime.datetime | None = None
    slug: str | None = None
    document: int | None = None
    file_version: ShareLinkFileVersion | None = None


class ShareLinkDraft(PaperlessModel, mixins.CreatableMixin):
    """Represent a new Paperless `ShareLink`, which is not stored in Paperless."""

    _api_path: ClassVar[str] = API_PATH["share_links"]

    _create_required_fields: ClassVar[set[str]] = {"document", "file_version"}

    expiration: datetime.datetime | None = None
    document: int | None = None
    file_version: ShareLinkFileVersion | None = None
