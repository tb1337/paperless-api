"""Model for document resource."""

from dataclasses import dataclass
from datetime import date, datetime

from .base import PaperlessModel, PaperlessPost
from .custom_fields import CustomFieldValue


@dataclass(kw_only=True)
class DocumentMetadata(PaperlessModel):
    """Represent a document metadata resource on the Paperless api."""

    namespace: str | None = None
    prefix: str | None = None
    key: str | None = None
    value: str | None = None


@dataclass(kw_only=True)
class DocumentMetaInformation(PaperlessModel):  # pylint: disable=too-many-instance-attributes
    """Represent a document metadata information resource on the Paperless api."""

    id: int | None = None
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


@dataclass(kw_only=True)
class DocumentNote(PaperlessModel):
    """Represent a document note resource on the Paperless api."""

    id: int | None = None
    note: str | None = None
    created: datetime | None = None
    document: int | None = None
    user: int | None = None


@dataclass(kw_only=True)
class DocumentNotePost(PaperlessPost):
    """Attributes to send when creating a document note on the Paperless api."""

    note: str
    document: int


@dataclass(kw_only=True)
class Document(PaperlessModel):  # pylint: disable=too-many-instance-attributes
    """Represent a document resource on the Paperless api."""

    id: int
    correspondent: int | None = None
    document_type: int | None = None
    storage_path: int | None = None
    title: str | None = None
    content: str | None = None
    tags: list[int] | None = None
    created: datetime | None = None
    created_date: date | None = None
    modified: datetime | None = None
    added: datetime | None = None
    archive_serial_number: int | None = None
    original_file_name: str | None = None
    archived_file_name: str | None = None
    owner: int | None = None
    user_can_change: bool | None = None
    notes: list[DocumentNote] | None = None
    custom_fields: list[CustomFieldValue] | None = None


@dataclass(kw_only=True)
class DocumentPost(PaperlessPost):  # pylint: disable=too-many-instance-attributes
    """Attributes to send when creating a document on the Paperless api."""

    document: bytes
    title: str | None = None
    created: datetime | None = None
    correspondent: int | None = None
    document_type: int | None = None
    storage_path: int | None = None
    tags: list[int] | None = None
    archive_serial_number: int | None = None
