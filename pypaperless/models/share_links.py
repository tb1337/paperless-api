"""Provide `ShareLink` related models and services."""

import datetime
from typing import TYPE_CHECKING, Any, ClassVar

from pypaperless.const import API_PATH, PaperlessResource

from .base import PaperlessModel, ServiceBase
from .common import ShareLinkFileVersionType
from .mixins import models, services

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
        self._format_api_path(data)


class ShareLinkDraft(PaperlessModel, models.CreatableMixin):
    """Represent a new Paperless `ShareLink`, which is not stored in Paperless."""

    _api_path: ClassVar[str] = API_PATH["share_links"]

    _create_required_fields: ClassVar[set[str]] = {"document", "file_version"}

    expiration: datetime.datetime | None = None
    document: int | None = None
    file_version: ShareLinkFileVersionType | None = None


class ShareLinkService(
    ServiceBase,
    services.CallableMixin[ShareLink],
    services.DraftableMixin[ShareLinkDraft],
    services.IterableMixin[ShareLink],
    services.UpdatableMixin[ShareLink],
    services.DeletableMixin[ShareLink],
):
    """Represent a factory for Paperless `ShareLink` models."""

    _api_path = API_PATH["share_links"]
    _resource = PaperlessResource.SHARE_LINKS

    _draft_cls = ShareLinkDraft
    _resource_cls = ShareLink
