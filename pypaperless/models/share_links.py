"""Model for share link resource."""

from dataclasses import dataclass
from datetime import datetime

from .base import PaperlessModel, PaperlessPost
from .shared import FileVersion


@dataclass(kw_only=True)
class ShareLink(PaperlessModel):
    """Represent a share link resource on the Paperless api."""

    id: int | None = None
    created: datetime | None = None
    expiration: datetime | None = None
    slug: str | None = None
    document: int | None = None
    file_version: FileVersion | None = None


@dataclass(kw_only=True)
class ShareLinkPost(PaperlessPost):
    """Attributes to send when creating a share link on the Paperless api."""

    expiration: datetime
    document: int
    file_version: FileVersion
