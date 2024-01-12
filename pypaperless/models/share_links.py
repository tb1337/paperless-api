"""Model for share link resource."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from .base import PaperlessModel, PaperlessPost


class ShareLinkFileVersion(Enum):
    """Enum with file version."""

    ARCHIVE = "archive"
    ORIGINAL = "original"
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls: type, value: object) -> "ShareLinkFileVersion":  # noqa ARG003
        """Set default member on unknown value."""
        return ShareLinkFileVersion.UNKNOWN


@dataclass(kw_only=True)
class ShareLink(PaperlessModel):
    """Represent a share link resource on the Paperless api."""

    id: int | None = None
    created: datetime | None = None
    expiration: datetime | None = None
    slug: str | None = None
    document: int | None = None
    file_version: ShareLinkFileVersion | None = None


@dataclass(kw_only=True)
class ShareLinkPost(PaperlessPost):
    """Attributes to send when creating a share link on the Paperless api."""

    expiration: datetime
    document: int
    file_version: ShareLinkFileVersion
