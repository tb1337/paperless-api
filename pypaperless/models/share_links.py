"""Provide `ShareLink` related models."""

import datetime
from typing import ClassVar

from pypaperless.const import API_PATH, PaperlessResource

from . import mixins
from .base import PaperlessModel
from .mixins.data_fields import EnumWithMissingFallback


class ShareLinkFileVersion(EnumWithMissingFallback):
    """Represent a subtype of `ShareLink`."""

    ARCHIVE = "archive"
    ORIGINAL = "original"
    UNKNOWN = "unknown"


class ShareLink(
    PaperlessModel,
    mixins.UpdatableMixin,
    mixins.DeletableMixin,
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


class ShareLinkDraft(PaperlessModel, mixins.CreatableMixin, mixins.SaveableMixin):
    """Represent a new Paperless `ShareLink`, which is not stored in Paperless."""

    _api_path: ClassVar[str] = API_PATH["share_links"]
    _resource: ClassVar[PaperlessResource] = PaperlessResource.SHARE_LINKS

    _create_required_fields: ClassVar[set[str]] = {"document", "file_version"}

    expiration: datetime.datetime | None = None
    document: int | None = None
    file_version: ShareLinkFileVersion | None = None
