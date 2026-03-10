"""Provide `ShareLink` related models."""

import datetime
from typing import TYPE_CHECKING, Any, ClassVar

from pypaperless.const import API_PATH

from . import mixins
from .base import PaperlessModel
from .common import ShareLinkFileVersionType

if TYPE_CHECKING:
    from pypaperless import Paperless


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
    file_version: ShareLinkFileVersionType | None = None

    def __init__(self, client: "Paperless", data: dict[str, Any], **kwargs: Any) -> None:
        """Initialize a `ShareLink` instance."""
        super().__init__(client, data, **kwargs)
        self._set_api_path(data)


class ShareLinkDraft(PaperlessModel, mixins.CreatableMixin):
    """Represent a new Paperless `ShareLink`, which is not stored in Paperless."""

    _api_path: ClassVar[str] = API_PATH["share_links"]

    _create_required_fields: ClassVar[set[str]] = {"document", "file_version"}

    expiration: datetime.datetime | None = None
    document: int | None = None
    file_version: ShareLinkFileVersionType | None = None
