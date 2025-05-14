"""Provide `ShareLink` related models and helpers."""

import datetime
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from pypaperless.const import API_PATH, PaperlessResource

from .base import HelperBase, PaperlessModel
from .common import ShareLinkFileVersionType
from .mixins import helpers, models

if TYPE_CHECKING:
    from pypaperless import Paperless


@dataclass(init=False)
class ShareLink(
    PaperlessModel,
    models.DeletableMixin,
    models.UpdatableMixin,
):
    """Represent a Paperless `ShareLink`."""

    _api_path = API_PATH["share_links_single"]

    id: int
    created: datetime.datetime | None = None
    expiration: datetime.datetime | None = None
    slug: str | None = None
    document: int | None = None
    file_version: ShareLinkFileVersionType | None = None

    def __init__(self, api: "Paperless", data: dict[str, Any]) -> None:
        """Initialize a `ShareLink` instance."""
        super().__init__(api, data)

        self._api_path = self._api_path.format(pk=data.get("id"))


@dataclass(init=False)
class ShareLinkDraft(
    PaperlessModel,
    models.CreatableMixin,
):
    """Represent a new Paperless `ShareLink`, which is not stored in Paperless."""

    _api_path = API_PATH["share_links"]

    _create_required_fields = {"document", "file_version"}

    expiration: datetime.datetime | None = None
    document: int | None = None
    file_version: ShareLinkFileVersionType | None = None


class ShareLinkHelper(
    HelperBase[ShareLink],
    helpers.CallableMixin[ShareLink],
    helpers.DraftableMixin[ShareLinkDraft],
    helpers.IterableMixin[ShareLink],
):
    """Represent a factory for Paperless `ShareLink` models."""

    _api_path = API_PATH["share_links"]
    _resource = PaperlessResource.SHARE_LINKS

    _draft_cls = ShareLinkDraft
    _resource_cls = ShareLink
