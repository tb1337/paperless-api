"""Provide `Document` related models."""

import datetime
import json
from collections.abc import AsyncGenerator, Iterator
from enum import StrEnum
from typing import TYPE_CHECKING, Any, ClassVar, Self, cast, overload

from pydantic import BaseModel, Field, PrivateAttr, ValidationInfo, field_validator

from pypaperless.const import API_PATH, PaperlessResource
from pypaperless.exceptions import ItemNotFoundError
from pypaperless.utils import object_to_dict_value

from . import mixins
from .base import PaperlessCustomDataModel, PaperlessModel
from .custom_fields import (
    CUSTOM_FIELD_TYPE_VALUE_MAP,
    CustomField,
    CustomFieldType,
    CustomFieldValue,
    CustomFieldValueT,
)

if TYPE_CHECKING:
    from pypaperless.services.documents import DocumentHistoryService, DocumentNoteService


class DocumentMetaEntry(BaseModel):
    """Represent a subtype of `DocumentMeta`."""

    namespace: str | None = None
    prefix: str | None = None
    key: str | None = None
    value: str | None = None


class DocumentSearchHit(BaseModel):
    """Represent a subtype of `Document`."""

    score: float | None = None
    highlights: str | None = None
    note_highlights: str | None = None
    rank: int | None = None


class FileRetrieveMode(StrEnum):
    """Represent a subtype of `DownloadedDocument`."""

    DOWNLOAD = "download"
    PREVIEW = "preview"
    THUMBNAIL = "thumb"


class DocumentHistoryAction(StrEnum):
    """Represent the action type of a `DocumentHistory` entry."""

    CREATE = "create"
    UPDATE = "update"


class DocumentHistoryActor(BaseModel):
    """Represent the actor field of a `DocumentHistory` entry."""

    id: int | None = None
    username: str | None = None


class DocumentHistory(PaperlessModel):
    """Represent a single Paperless document history (audit-log) entry."""

    _api_path: ClassVar[str] = API_PATH["documents_history"]

    id: int | None = None
    document: int | None = None
    timestamp: datetime.datetime | None = None
    action: DocumentHistoryAction | None = None
    changes: dict[str, Any] = Field(default_factory=dict)
    actor: DocumentHistoryActor | None = None


class DocumentCustomFieldList(PaperlessCustomDataModel):
    """Represent a list of Paperless custom field instances typically on documents."""

    _fields: list[CustomFieldValue] = PrivateAttr(default_factory=list)

    def model_post_init(self, __context: Any, /) -> None:
        """Populate ``_fields`` from the raw API payload stored in ``_data``."""
        super().model_post_init(__context)
        self._fields = []

        cache = self._client.cache.custom_fields

        for item in self._data:
            if cache and (field := cache.get(item["field"], None)):
                klass = CUSTOM_FIELD_TYPE_VALUE_MAP.get(
                    field.data_type or CustomFieldType.UNKNOWN, CustomFieldValue
                )
                klass_data = {
                    **item,
                    "name": field.name,
                    "data_type": field.data_type,
                    "extra_data": field.extra_data,
                }
                self._fields.append(klass(**klass_data))
            else:
                self._fields.append(CustomFieldValue(**item))

    def __contains__(self, field: int | CustomField) -> bool:
        """Check if the given `CustomField` or its id is present in `DocumentCustomFieldList`."""
        item_id = field.id if isinstance(field, CustomField) else field
        return any(item.field == item_id for item in self._fields)

    def __iter__(self) -> Iterator[CustomFieldValue]:  # type: ignore[override]
        """Iterate over custom fields.

        This intentionally behaves like a container iterator (yielding
        ``CustomFieldValue`` items) instead of Pydantic's field-pair iterator.

        Example:
        -------
        ```python
        for item in document.custom_fields:
            # do something
        ```

        """
        yield from self._fields

    def __iadd__(self, field: CustomFieldValue) -> Self:
        """Add a new `CustomFieldValue` to a document."""
        return self.add(field)

    def add(self, field: CustomFieldValue) -> Self:
        """Add a new `CustomFieldValue` to a document."""
        self._fields.append(field)
        return self

    def __isub__(self, field: CustomFieldValue | CustomField | int) -> Self:
        """Remove a `CustomFieldValue` from a document."""
        return self.remove(field)

    def remove(self, field: CustomFieldValue | CustomField | int) -> Self:
        """Remove a `CustomFieldValue` from a document."""
        item_id = (
            field.id
            if isinstance(field, CustomField)
            else field.field
            if isinstance(field, CustomFieldValue)
            else field
        )
        self._fields = [field for field in self._fields if field.field != item_id]
        return self

    @overload
    def default(self, field: int | CustomField) -> CustomFieldValue | None: ...

    @overload
    def default(
        self, field: int | CustomField, expected_type: type[CustomFieldValueT]
    ) -> CustomFieldValueT | None: ...

    def default(
        self, field: int | CustomField, expected_type: type[CustomFieldValueT] | None = None
    ) -> CustomFieldValue | CustomFieldValueT | None:
        """Access and return a (typed) `CustomFieldValue`, or `None`."""
        try:
            value = self.get(field)
        except ItemNotFoundError:
            return None

        if expected_type is not None and not isinstance(value, expected_type):
            msg = f"Expected {expected_type.__name__}, got {type(value).__name__}"
            raise TypeError(msg)

        return value

    @overload
    def get(self, field: int | CustomField) -> CustomFieldValue: ...

    @overload
    def get(
        self, field: int | CustomField, expected_type: type[CustomFieldValueT]
    ) -> CustomFieldValueT: ...

    def get(
        self, field: int | CustomField, expected_type: type[CustomFieldValueT] | None = None
    ) -> CustomFieldValue | CustomFieldValueT:
        """Access and return a (typed) `CustomFieldValue` from the list."""
        item_id = field.id if isinstance(field, CustomField) else field
        for item in self._fields:
            if item.field == item_id:
                if expected_type is not None and not isinstance(item, expected_type):
                    msg = f"Expected {expected_type.__name__}, got {type(item).__name__}"
                    raise TypeError(msg)
                return item
        raise ItemNotFoundError

    def serialize(self) -> list[dict[str, Any]]:
        """Serialize the class data."""
        return [{"field": field.field, "value": field.value} for field in self._fields]


class Document(
    PaperlessModel,
    mixins.SecurableMixin,
    mixins.UpdatableMixin,
    mixins.DeletableMixin,
):
    """Represent a Paperless `Document`."""

    _api_path: ClassVar[str] = API_PATH["documents_single"]
    _resource: ClassVar[PaperlessResource] = PaperlessResource.DOCUMENTS

    _history: "DocumentHistoryService | None" = PrivateAttr(default=None)
    _notes: "DocumentNoteService | None" = PrivateAttr(default=None)

    id: int | None = None
    correspondent: int | None = None
    document_type: int | None = None
    storage_path: int | None = None
    title: str | None = None
    content: str | None = None
    tags: list[int] | None = None
    created: datetime.date | None = None
    modified: datetime.datetime | None = None
    added: datetime.datetime | None = None
    deleted_at: datetime.datetime | None = None
    archive_serial_number: int | None = None
    original_file_name: str | None = None
    archived_file_name: str | None = None
    is_shared_by_requester: bool | None = None
    custom_fields: DocumentCustomFieldList | list | None = None
    page_count: int | None = None
    mime_type: str | None = None
    search_hit_: DocumentSearchHit | None = Field(default=None, alias="__search_hit__")

    @field_validator("custom_fields", mode="before")
    @classmethod
    def _coerce_custom_fields(cls, v: Any, info: ValidationInfo) -> Any:
        """Convert a raw list of custom field dicts into a ``DocumentCustomFieldList``."""
        if isinstance(v, list) and isinstance(info.context, dict) and "client" in info.context:
            return DocumentCustomFieldList.from_data(info.context["client"], v)
        return v

    @property
    def history(self) -> "DocumentHistoryService":
        """Return the history service for this document."""
        if self._history is None:
            from pypaperless.services.documents import DocumentHistoryService  # noqa: PLC0415

            self._history = DocumentHistoryService(self._client, cast("int", self.id))
        return self._history

    @property
    def notes(self) -> "DocumentNoteService":
        """Return the notes helper for this document."""
        if self._notes is None:
            from pypaperless.services.documents import DocumentNoteService  # noqa: PLC0415

            self._notes = DocumentNoteService(self._client, cast("int", self.id))
        return self._notes

    async def download(self, *, original: bool = False) -> "DownloadedDocument":
        """Shortcut for ``paperless.documents.download(self.id)``."""
        return await self._client.documents.download(cast("int", self.id), original=original)

    async def preview(self, *, original: bool = False) -> "DownloadedDocument":
        """Shortcut for ``paperless.documents.preview(self.id)``."""
        return await self._client.documents.preview(cast("int", self.id), original=original)

    async def thumbnail(self, *, original: bool = False) -> "DownloadedDocument":
        """Shortcut for ``paperless.documents.thumbnail(self.id)``."""
        return await self._client.documents.thumbnail(cast("int", self.id), original=original)

    async def metadata(self) -> "DocumentMeta":
        """Shortcut for ``paperless.documents.metadata(self.id)``."""
        return await self._client.documents.metadata(cast("int", self.id))

    async def suggestions(self) -> "DocumentSuggestions":
        """Shortcut for ``paperless.documents.suggestions(self.id)``."""
        return await self._client.documents.suggestions(cast("int", self.id))

    async def more_like(self) -> AsyncGenerator["Document"]:
        """Shortcut for ``paperless.documents.more_like(self.id)``."""
        async for doc in self._client.documents.more_like(cast("int", self.id)):
            yield doc

    async def email(
        self,
        *,
        addresses: str,
        subject: str,
        message: str,
        use_archive_version: bool = True,
    ) -> None:
        """Shortcut for ``paperless.documents.email(self.id, ...)``."""
        await self._client.documents.email(
            cast("int", self.id),
            addresses=addresses,
            subject=subject,
            message=message,
            use_archive_version=use_archive_version,
        )

    @property
    def created_date(self) -> datetime.date | None:
        """Backward compatibility for the removed `created_date` field."""
        return self.created

    @property
    def is_deleted(self) -> bool:
        """Return True if the document is in the trash."""
        return self.deleted_at is not None

    @property
    def has_search_hit(self) -> bool:
        """Return if the document has a search hit attached."""
        return self.search_hit_ is not None

    @property
    def search_hit(self) -> DocumentSearchHit | None:
        """Return the document search hit."""
        return self.search_hit_

    def apply_data(self) -> None:
        """Apply data from `self._data` to model fields, converting custom_fields."""
        super().apply_data()
        if "custom_fields" in self._data and isinstance(self._data["custom_fields"], list):
            self.custom_fields = DocumentCustomFieldList.from_data(
                self._client, self._data["custom_fields"]
            )


class DocumentDraft(PaperlessModel, mixins.CreatableMixin, mixins.SaveableMixin):
    """Represent a new Paperless `Document`, which is not stored in Paperless."""

    _api_path: ClassVar[str] = API_PATH["documents_post"]
    _resource: ClassVar[PaperlessResource] = PaperlessResource.DOCUMENTS

    _create_required_fields: ClassVar[set[str]] = {"document"}

    document: bytes | None = None
    filename: str | None = None
    title: str | None = None
    created: datetime.datetime | None = None
    correspondent: int | None = None
    document_type: int | None = None
    storage_path: int | None = None
    tags: int | list[int] | None = None
    archive_serial_number: int | None = None
    custom_fields: list[int] | DocumentCustomFieldList | None = None

    def serialize(self) -> dict[str, Any]:
        """Serialize."""
        data = {
            "form": {
                name: object_to_dict_value(getattr(self, name))
                for name in self.__class__.model_fields
                if name not in {"document", "filename", "custom_fields"}
            }
        }

        if self.custom_fields is not None:
            if isinstance(self.custom_fields, DocumentCustomFieldList):
                cf_map = {
                    str(item["field"]): item["value"] for item in self.custom_fields.serialize()
                }
                data["form"]["custom_fields"] = json.dumps(cf_map)
            else:
                data["form"]["custom_fields"] = self.custom_fields

        data["form"].update(
            {
                "document": (
                    (self.document, self.filename) if self.filename is not None else self.document
                )
            }
        )
        return data


class DocumentNote(PaperlessModel):
    """Represent a Paperless `DocumentNote`."""

    _api_path: ClassVar[str] = API_PATH["documents_notes"]
    _pk_field: ClassVar[str] = "document"

    id: int | None = None
    note: str | None = None
    created: datetime.datetime | None = None
    document: int | None = None
    user: int | None = None

    async def delete(self) -> bool:
        """Shortcut for ``paperless.documents.notes.delete(self)``."""
        return await self._client.documents.notes.delete(self)


class DocumentNoteDraft(PaperlessModel, mixins.CreatableMixin):
    """Represent a new Paperless `DocumentNote`, which is not stored in Paperless."""

    _api_path: ClassVar[str] = API_PATH["documents_notes"]
    _pk_field: ClassVar[str] = "document"

    _create_required_fields: ClassVar[set[str]] = {"note", "document"}

    note: str | None = None
    document: int | None = None

    async def save(self) -> tuple[int, int]:
        """Shortcut for ``paperless.documents.notes.save(self)``."""
        return await self._client.documents.notes.save(self)


class DocumentMeta(PaperlessModel):
    """Represent a Paperless `Document`s metadata."""

    _api_path: ClassVar[str] = API_PATH["documents_meta"]

    id: int | None = None
    original_checksum: str | None = None
    original_size: int | None = None
    original_mime_type: str | None = None
    media_filename: str | None = None
    has_archive_version: bool | None = None
    original_metadata: list[DocumentMetaEntry] | None = None
    archive_checksum: str | None = None
    archive_media_filename: str | None = None
    original_filename: str | None = None
    lang: str | None = None
    archive_size: int | None = None
    archive_metadata: list[DocumentMetaEntry] | None = None


class DownloadedDocument(PaperlessModel):
    """Represent a Paperless `Document`s downloaded file."""

    _api_path: ClassVar[str] = API_PATH["documents"]

    id: int | None = None
    mode: FileRetrieveMode | None = None
    original: bool | None = None
    content: bytes | None = None
    content_type: str | None = None
    disposition_filename: str | None = None
    disposition_type: str | None = None


class DocumentSuggestions(PaperlessModel):
    """Represent a Paperless `Document` suggestions."""

    _api_path: ClassVar[str] = API_PATH["documents_suggestions"]

    id: int | None = None
    correspondents: list[int] | None = None
    tags: list[int] | None = None
    document_types: list[int] | None = None
    storage_paths: list[int] | None = None
    dates: list[datetime.date] | None = None
