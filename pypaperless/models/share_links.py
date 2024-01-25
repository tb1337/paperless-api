"""Provide `ShareLink` related models and helpers."""

import datetime
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, final

from pypaperless.const import API_PATH

from .base import HelperBase, PaperlessModel
from .common import ShareLinkFileVersionType
from .mixins import helpers, models

if TYPE_CHECKING:
    from pypaperless import Paperless


@final
@dataclass(init=False)
class ShareLink(PaperlessModel):  # pylint: disable=too-many-instance-attributes
    """Represent a Paperless `ShareLink`."""

    _api_path = API_PATH["share_links_single"]

    id: int
    created: datetime.datetime | None = None
    expiration: datetime.datetime | None = None
    slug: str | None = None
    document: int | None = None
    file_version: ShareLinkFileVersionType | None = None

    def __init__(self, api: "Paperless", data: dict[str, Any]):
        """Initialize a `MailAccount` instance."""
        super().__init__(api, data)

        self._api_path = self._api_path.format(pk=data.get("id"))


@final
@dataclass(init=False)
class ShareLinkDraft(
    PaperlessModel,
    models.CreatableMixin,
):
    """Represent a new Paperless `ShareLink`, which is not stored in Paperless."""

    _api_path = API_PATH["share_links"]

    _create_required_fields = {"expiration", "document", "file_version"}

    expiration: datetime.datetime | None = None
    document: int | None = None
    file_version: ShareLinkFileVersionType | None = None


@final
class ShareLinkHelper(  # pylint: disable=too-many-ancestors
    HelperBase[ShareLink],
    helpers.CallableMixin[ShareLink],
    helpers.DraftableMixin[ShareLinkDraft],
    helpers.IterableMixin[ShareLink],
):
    """Represent a factory for Paperless `ShareLink` models."""

    _api_path = API_PATH["share_links"]

    _resource = ShareLink
