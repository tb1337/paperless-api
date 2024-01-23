"""Provide the `Documents` class."""

import datetime
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, final

from pypaperless.const import API_PATH

from .base import PaperlessModel
from .mixins import CreatableMixin, DeletableMixin, UpdatableMixin

if TYPE_CHECKING:
    from pypaperless import Paperless


@final
@dataclass(init=False)
class Document(
    PaperlessModel,
    UpdatableMixin,
    DeletableMixin,
):  # pylint: disable=too-many-instance-attributes
    """Represent a Paperless `Document`."""

    _api_path = API_PATH["documents_single"]

    id: int
    correspondent: int | None = None
    document_type: int | None = None
    storage_path: int | None = None
    title: str | None = None
    content: str | None = None
    tags: list[int] | None = None
    created: datetime.datetime | None = None
    created_date: datetime.date | None = None
    modified: datetime.datetime | None = None
    added: datetime.datetime | None = None
    archive_serial_number: int | None = None
    original_file_name: str | None = None
    archived_file_name: str | None = None
    owner: int | None = None
    user_can_change: bool | None = None
    notes: list[dict[str, Any]] | None = None
    custom_fields: list[dict[str, Any]] | None = None

    def __init__(self, api: "Paperless", data: dict[str, Any]):
        """Initialize a `Document` instance."""
        super().__init__(api, data)

        self._api_path = self._api_path.format(pk=data.get("id"))

    async def get_metadata(self) -> "DocumentMeta":
        """Return the documents `DocumentMeta` class."""
        return await self._api.documents.metadata(self.id)


@final
@dataclass(init=False)
class DocumentDraft(
    PaperlessModel,
    CreatableMixin,
):  # pylint: disable=too-many-instance-attributes
    """Represent a new Paperless `Document`, which is not stored in Paperless."""

    _api_path = API_PATH["documents_post"]

    _create_required_fields = {"document"}

    document: bytes | None = None
    title: str | None = None
    created: datetime.datetime | None = None
    correspondent: int | None = None
    document_type: int | None = None
    storage_path: int | None = None
    tags: list[int] | None = None
    archive_serial_number: int | None = None


@final
@dataclass(kw_only=True)
class DocumentMetadata:
    """Represent a subtype of `DocumentMeta`."""

    namespace: str | None = None
    prefix: str | None = None
    key: str | None = None
    value: str | None = None


@final
@dataclass(init=False)
class DocumentMeta(PaperlessModel):  # pylint: disable=too-many-instance-attributes
    """Represent a Paperless `Document`s metadata."""

    _api_path = API_PATH["documents_meta"]

    id: int
    original_checksum: str | None = None
    original_size: int | None = None
    original_mime_type: str | None = None
    media_filename: str | None = None
    has_archive_version: bool | None = None
    original_metadata: list[DocumentMetadata] | None = None
    archive_checksum: str | None = None
    archive_media_filename: str | None = None
    original_filename: str | None = None
    lang: str | None = None
    archive_size: int | None = None
    archive_metadata: list[DocumentMetadata] | None = None

    def __init__(self, api: "Paperless", data: dict[str, Any]):
        """Initialize a `DocumentMeta` instance."""
        super().__init__(api, data)

        self._api_path = self._api_path.format(pk=data.get("id"))
