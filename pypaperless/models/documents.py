"""Provide `Document` related models and helpers."""

import datetime
from collections.abc import AsyncGenerator, Iterator
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Self, cast

from pypaperless.const import API_PATH, PaperlessResource
from pypaperless.exceptions import AsnRequestError, ItemNotFoundError, PrimaryKeyRequiredError
from pypaperless.models.utils import object_to_dict_value

from .base import HelperBase, PaperlessModel, PaperlessModelData
from .common import (
    CustomFieldBooleanValue,
    CustomFieldDateValue,
    CustomFieldDocumentLinkValue,
    CustomFieldFloatValue,
    CustomFieldIntegerValue,
    CustomFieldSelectValue,
    CustomFieldStringValue,
    CustomFieldType,
    CustomFieldValue,
    DocumentMetadataType,
    DocumentSearchHitType,
    RetrieveFileMode,
)
from .custom_fields import CustomField
from .mixins import helpers, models

if TYPE_CHECKING:
    from pypaperless import Paperless


class DocumentCustomFieldList(PaperlessModelData):
    """Represent a list of Paperless custom field instances typically on documents."""

    CustomFieldValueMap: dict[CustomFieldType, type[CustomFieldValue]] = {
        CustomFieldType.BOOLEAN: CustomFieldBooleanValue,
        CustomFieldType.DATE: CustomFieldDateValue,
        CustomFieldType.DOCUMENT_LINK: CustomFieldDocumentLinkValue,
        CustomFieldType.FLOAT: CustomFieldFloatValue,
        CustomFieldType.INTEGER: CustomFieldIntegerValue,
        CustomFieldType.SELECT: CustomFieldSelectValue,
        CustomFieldType.STRING: CustomFieldStringValue,
    }

    def __init__(self, api: "Paperless", data: list[dict[str, Any]]) -> None:
        """Initialize a `CustomFieldList` instance."""
        self._api = api
        self._data = data
        self._fields: list[CustomFieldValue] = []

        cache = api.cache.custom_fields

        for item in data:
            if cache and (field := cache.get(item["field"], None)):
                klass = self.CustomFieldValueMap.get(
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
        return any(item["field"] == item_id for item in self._data)

    def __iter__(self) -> Iterator[CustomFieldValue]:
        """Iterate over custom fields.

        Example:
        -------
        ```python
        for item in document.custom_fields:
            # do something
        ```

        """
        yield from self._fields

    def default(self, field: int | CustomField) -> CustomFieldValue | None:
        """Access and return a `CustomField` from the `DocumentCustomFieldList`, or `None`."""
        try:
            return self.get(field)
        except ItemNotFoundError:
            return None

    def get(self, field: int | CustomField) -> CustomFieldValue:
        """Access and return a `CustomField` from the `DocumentCustomFieldList`, or raise."""
        item_id = field.id if isinstance(field, CustomField) else field

        for item in self._fields:
            if item.field == item_id:
                return item
        raise ItemNotFoundError

    @classmethod
    def unserialize(cls, api: "Paperless", data: list[dict[str, Any]]) -> Self:
        """Return a new instance of `cls` from `data`.

        Primarily used by `dict_value_to_object` when instantiating model classes.
        """
        return cls(api, data=data)

    def serialize(self) -> list[dict[str, Any]]:
        """Serialize the class data."""
        return self._data


@dataclass(init=False)
class Document(
    PaperlessModel,
    models.SecurableMixin,
    models.UpdatableMixin,
    models.DeletableMixin,
):
    """Represent a Paperless `Document`."""

    _api_path = API_PATH["documents_single"]

    id: int | None = None
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
    deleted_at: datetime.datetime | None = None
    archive_serial_number: int | None = None
    original_file_name: str | None = None
    archived_file_name: str | None = None
    is_shared_by_requester: bool | None = None
    custom_fields: DocumentCustomFieldList | None = None
    page_count: int | None = None
    mime_type: str | None = None
    __search_hit__: DocumentSearchHitType | None = None

    def __init__(self, api: "Paperless", data: dict[str, Any]) -> None:
        """Initialize a `Document` instance."""
        super().__init__(api, data)

        self._api_path = self._api_path.format(pk=data.get("id"))
        self.notes = DocumentNoteHelper(api, data.get("id"))

    @property
    def has_search_hit(self) -> bool:
        """Return if the document has a search hit attached."""
        return self.__search_hit__ is not None

    @property
    def search_hit(self) -> DocumentSearchHitType | None:
        """Return the document search hit."""
        return self.__search_hit__

    async def get_download(self, *, original: bool = False) -> "DownloadedDocument":
        """Request and return the `DownloadedDocument` class."""
        return await self._api.documents.download(cast("int", self.id), original=original)

    async def get_metadata(self) -> "DocumentMeta":
        """Request and return the documents `DocumentMeta` class."""
        return await self._api.documents.metadata(cast("int", self.id))

    async def get_preview(self, *, original: bool = False) -> "DownloadedDocument":
        """Request and return the `DownloadedDocument` class."""
        return await self._api.documents.preview(cast("int", self.id), original=original)

    async def get_suggestions(self) -> "DocumentSuggestions":
        """Request and return the `DocumentSuggestions` class."""
        return await self._api.documents.suggestions(cast("int", self.id))

    async def get_thumbnail(self, *, original: bool = False) -> "DownloadedDocument":
        """Request and return the `DownloadedDocument` class."""
        return await self._api.documents.thumbnail(cast("int", self.id), original=original)


@dataclass(init=False)
class DocumentDraft(
    PaperlessModel,
    models.CreatableMixin,
):
    """Represent a new Paperless `Document`, which is not stored in Paperless."""

    _api_path = API_PATH["documents_post"]

    _create_required_fields = {"document"}

    document: bytes | None = None
    filename: str | None = None
    title: str | None = None
    created: datetime.datetime | None = None
    correspondent: int | None = None
    document_type: int | None = None
    storage_path: int | None = None
    tags: int | list[int] | None = None
    archive_serial_number: int | None = None
    custom_fields: list[int] | None = None

    def _serialize(self) -> dict[str, Any]:
        """Serialize."""
        data = {
            "form": {
                field.name: object_to_dict_value(getattr(self, field.name))
                for field in self._get_dataclass_fields()
                if field.name not in {"document", "filename"}
            }
        }
        data["form"].update(
            {
                "document": (
                    (self.document, self.filename) if self.filename is not None else self.document
                )
            }
        )
        return data


@dataclass(init=False)
class DocumentNote(PaperlessModel):
    """Represent a Paperless `DocumentNote`."""

    _api_path = API_PATH["documents_notes"]

    id: int | None = None
    note: str | None = None
    created: datetime.datetime | None = None
    document: int | None = None
    user: int | None = None

    def __init__(self, api: "Paperless", data: dict[str, Any]) -> None:
        """Initialize a `DocumentNote` instance."""
        super().__init__(api, data)

        self._api_path = self._api_path.format(pk=data.get("document"))

    async def delete(self) -> bool:
        """Delete a `resource item` from DRF. There is no point of return.

        Return `True` when deletion was successful, `False` otherwise.

        Example:
        -------
        ```python
        # request document notes
        notes = await paperless.documents.notes(42)

        for note in notes:
            if await note.delete():
                print("Successfully deleted the note!")
        ```

        """
        params = {
            "id": self.id,
        }
        async with self._api.request("delete", self._api_path, params=params) as res:
            return res.status == 204


@dataclass(kw_only=True)
class DocumentNoteDraft(
    PaperlessModel,
    models.CreatableMixin,
):
    """Represent a new Paperless `DocumentNote`, which is not stored in Paperless."""

    _api_path = API_PATH["documents_notes"]

    _create_required_fields = {"note", "document"}

    note: str | None = None
    document: int | None = None

    def __init__(self, api: "Paperless", data: dict[str, Any]) -> None:
        """Initialize a `DocumentNote` instance."""
        super().__init__(api, data)

        self._api_path = self._api_path.format(pk=data.get("document"))


@dataclass(init=False)
class DocumentMeta(PaperlessModel):
    """Represent a Paperless `Document`s metadata."""

    _api_path = API_PATH["documents_meta"]

    id: int | None = None
    original_checksum: str | None = None
    original_size: int | None = None
    original_mime_type: str | None = None
    media_filename: str | None = None
    has_archive_version: bool | None = None
    original_metadata: list[DocumentMetadataType] | None = None
    archive_checksum: str | None = None
    archive_media_filename: str | None = None
    original_filename: str | None = None
    lang: str | None = None
    archive_size: int | None = None
    archive_metadata: list[DocumentMetadataType] | None = None

    def __init__(self, api: "Paperless", data: dict[str, Any]) -> None:
        """Initialize a `DocumentMeta` instance."""
        super().__init__(api, data)

        self._api_path = self._api_path.format(pk=data.get("id"))


@dataclass(init=False)
class DownloadedDocument(PaperlessModel):
    """Represent a Paperless `Document`s downloaded file."""

    _api_path = API_PATH["documents"]

    id: int | None = None
    mode: RetrieveFileMode | None = None
    original: bool | None = None
    content: bytes | None = None
    content_type: str | None = None
    disposition_filename: str | None = None
    disposition_type: str | None = None

    async def load(self) -> None:
        """Get `raw data` from DRF."""
        self._api_path = self._api_path.format(pk=self._data.get("id"))

        params = {
            "original": "true" if self._data.get("original", False) else "false",
        }

        async with self._api.request("get", self._api_path, params=params) as res:
            self._data.update(
                {
                    "content": await res.read(),
                    "content_type": res.content_type,
                }
            )

            if res.content_disposition is not None:
                self._data.update(
                    {
                        "disposition_filename": res.content_disposition.filename,
                        "disposition_type": res.content_disposition.type,
                    }
                )

        self._set_dataclass_fields()
        self._fetched = True


@dataclass(init=False)
class DocumentSuggestions(PaperlessModel):
    """Represent a Paperless `Document` suggestions."""

    _api_path = API_PATH["documents_suggestions"]

    id: int | None = None
    correspondents: list[int] | None = None
    tags: list[int] | None = None
    document_types: list[int] | None = None
    storage_paths: list[int] | None = None
    dates: list[datetime.date] | None = None

    def __init__(self, api: "Paperless", data: dict[str, Any]) -> None:
        """Initialize a `DocumentSuggestions` instance."""
        super().__init__(api, data)

        self._api_path = self._api_path.format(pk=data.get("id"))


class DocumentSuggestionsHelper(HelperBase[DocumentSuggestions]):
    """Represent a factory for Paperless `DocumentSuggestions` models."""

    _api_path = API_PATH["documents_suggestions"]
    _resource = PaperlessResource.DOCUMENTS

    _resource_cls = DocumentSuggestions

    async def __call__(self, pk: int) -> DocumentSuggestions:
        """Request exactly one resource item."""
        data = {
            "id": pk,
        }
        item = self._resource_cls.create_with_data(self._api, data)
        await item.load()

        return item


class DocumentSubHelperBase(
    HelperBase[DownloadedDocument],
):
    """Represent a factory for Paperless `DownloadedDocument` models."""

    _api_path = API_PATH["documents_suggestions"]
    _resource = PaperlessResource.DOCUMENTS

    _resource_cls = DownloadedDocument

    async def __call__(
        self,
        pk: int,
        mode: RetrieveFileMode,
        api_path: str,
        *,
        original: bool,
    ) -> DownloadedDocument:
        """Request exactly one resource item."""
        data = {
            "id": pk,
            "mode": mode,
            "original": original,
        }
        item = self._resource_cls.create_with_data(self._api, data)
        item._api_path = api_path  # noqa: SLF001
        await item.load()

        return item


class DocumentFileDownloadHelper(DocumentSubHelperBase):
    """Represent a factory for Paperless `DownloadedDocument` models."""

    _api_path = API_PATH["documents_download"]

    async def __call__(  # type: ignore[override]
        self,
        pk: int,
        *,
        original: bool = False,
    ) -> DownloadedDocument:
        """Request exactly one resource item."""
        return await super().__call__(
            pk, RetrieveFileMode.DOWNLOAD, self._api_path, original=original
        )


class DocumentFilePreviewHelper(DocumentSubHelperBase):
    """Represent a factory for Paperless `DownloadedDocument` models."""

    _api_path = API_PATH["documents_preview"]

    async def __call__(  # type: ignore[override]
        self,
        pk: int,
        *,
        original: bool = False,
    ) -> DownloadedDocument:
        """Request exactly one resource item."""
        return await super().__call__(
            pk, RetrieveFileMode.PREVIEW, self._api_path, original=original
        )


class DocumentFileThumbnailHelper(DocumentSubHelperBase):
    """Represent a factory for Paperless `DownloadedDocument` models."""

    _api_path = API_PATH["documents_thumbnail"]

    async def __call__(  # type: ignore[override]
        self,
        pk: int,
        *,
        original: bool = False,
    ) -> DownloadedDocument:
        """Request exactly one resource item."""
        return await super().__call__(
            pk, RetrieveFileMode.THUMBNAIL, self._api_path, original=original
        )


class DocumentMetaHelper(
    HelperBase[DocumentMeta],
    helpers.CallableMixin[DocumentMeta],
):
    """Represent a factory for Paperless `DocumentMeta` models."""

    _api_path = API_PATH["documents_meta"]
    _resource = PaperlessResource.DOCUMENTS

    _resource_cls = DocumentMeta


class DocumentNoteHelper(HelperBase[DocumentNote]):
    """Represent a factory for Paperless `DocumentNote` models."""

    _api_path = API_PATH["documents_notes"]
    _resource = PaperlessResource.DOCUMENTS

    _resource_cls = DocumentNote

    def __init__(self, api: "Paperless", attached_to: int | None = None) -> None:
        """Initialize a `DocumentHelper` instance."""
        super().__init__(api)

        self._attached_to = attached_to

    async def __call__(
        self,
        pk: int | None = None,
    ) -> list[DocumentNote]:
        """Request and return the documents `DocumentNote` list."""
        doc_pk = self._get_document_pk(pk)
        res = await self._api.request_json("get", self._get_api_path(doc_pk))

        # We have to transform data here slightly.
        # There are two major differences in the data depending on which endpoint is requested.
        # url: documents/{:pk}/ ->
        #       .document -> int
        #       .user -> int
        # url: documents/{:pk}/notes/ ->
        #       .document -> does not exist (so we add it here)
        #       .user -> dict(id=int, username=str, first_name=str, last_name=str)
        return [
            self._resource_cls.create_with_data(
                self._api,
                {
                    **item,
                    "document": doc_pk,
                    "user": item["user"]["id"],
                },
                fetched=True,
            )
            for item in res
        ]

    def _get_document_pk(self, pk: int | None = None) -> int:
        """Return the attached document pk, or the parameter."""
        if not any((self._attached_to, pk)):
            message = f"Accessing {type(self).__name__} data without a primary key."
            raise PrimaryKeyRequiredError(message)
        return cast("int", self._attached_to or pk)

    def _get_api_path(self, pk: int) -> str:
        """Return the formatted api path."""
        return self._api_path.format(pk=pk)

    def draft(self, pk: int | None = None, **kwargs: Any) -> DocumentNoteDraft:
        """Return a fresh and empty `DocumentNoteDraft` instance.

        Example:
        -------
        ```python
        draft = paperless.documents.notes.draft(...)
        # do something
        ```

        """
        kwargs.update({"document": self._get_document_pk(pk)})
        return DocumentNoteDraft.create_with_data(
            self._api,
            data=kwargs,
            fetched=True,
        )


class DocumentHelper(
    HelperBase[Document],
    helpers.SecurableMixin,
    helpers.CallableMixin[Document],
    helpers.DraftableMixin[DocumentDraft],
    helpers.IterableMixin[Document],
):
    """Represent a factory for Paperless `Document` models."""

    _api_path = API_PATH["documents"]
    _resource = PaperlessResource.DOCUMENTS

    _draft_cls = DocumentDraft
    _resource_cls = Document

    def __init__(self, api: "Paperless") -> None:
        """Initialize a `DocumentHelper` instance."""
        super().__init__(api)

        self._download = DocumentFileDownloadHelper(api)
        self._meta = DocumentMetaHelper(api)
        self._notes = DocumentNoteHelper(api)
        self._preview = DocumentFilePreviewHelper(api)
        self._suggestions = DocumentSuggestionsHelper(api)
        self._thumbnail = DocumentFileThumbnailHelper(api)

    @property
    def download(self) -> DocumentFileDownloadHelper:
        """Download the contents of an archived file.

        Example:
        -------
        ```python
        # request document contents directly...
        download = await paperless.documents.download(42)

        # ... or by using an already fetched document
        doc = await paperless.documents(42)

        download = await doc.get_download()
        ```

        """
        return self._download

    @property
    def metadata(self) -> DocumentMetaHelper:
        """Return the attached `DocumentMetaHelper` instance.

        Example:
        -------
        ```python
        # request metadata of a document directly...
        metadata = await paperless.documents.metadata(42)

        # ... or by using an already fetched document
        doc = await paperless.documents(42)
        metadata = await doc.get_metadata()
        ```

        """
        return self._meta

    @property
    def notes(self) -> DocumentNoteHelper:
        """Return the attached `DocumentNoteHelper` instance.

        Example:
        -------
        ```python
        # request document notes directly...
        notes = await paperless.documents.notes(42)

        # ... or by using an already fetched document
        doc = await paperless.documents(42)
        notes = await doc.notes()
        ```

        """
        return self._notes

    @property
    def preview(self) -> DocumentFilePreviewHelper:
        """Preview the contents of an archived file.

        Example:
        -------
        ```python
        # request document contents directly...
        download = await paperless.documents.preview(42)

        # ... or by using an already fetched document
        doc = await paperless.documents(42)

        download = await doc.get_preview()
        ```

        """
        return self._preview

    @property
    def suggestions(self) -> DocumentSuggestionsHelper:
        """Return the attached `DocumentSuggestionsHelper` instance.

        Example:
        -------
        ```python
        # request document suggestions directly...
        suggestions = await paperless.documents.suggestions(42)

        # ... or by using an already fetched document
        doc = await paperless.suggestions(42)

        suggestions = await doc.get_suggestions()
        ```

        """
        return self._suggestions

    @property
    def thumbnail(self) -> DocumentFileThumbnailHelper:
        """Download the contents of a thumbnail file.

        Example:
        -------
        ```python
        # request document contents directly...
        download = await paperless.documents.thumbnail(42)

        # ... or by using an already fetched document
        doc = await paperless.documents(42)

        download = await doc.get_thumbnail()
        ```

        """
        return self._thumbnail

    async def get_next_asn(self) -> int:
        """Request the next archive serial number from DRF."""
        async with self._api.request("get", API_PATH["documents_next_asn"]) as res:
            try:
                res.raise_for_status()
                return int(await res.text())
            except Exception as exc:
                raise AsnRequestError from exc

    async def more_like(self, pk: int) -> AsyncGenerator[Document]:
        """Lookup documents similar to the given document pk.

        Shortcut function. Same behaviour is possible using `reduce()`.

        Documentation: https://docs.paperless-ngx.com/api/#searching-for-documents
        """
        async with self.reduce(more_like_id=pk):
            async for item in self:
                yield item

    async def search(self, query: str) -> AsyncGenerator[Document]:
        """Lookup documents by a search query.

        Shortcut function. Same behaviour is possible using `reduce()`.

        Documentation: https://docs.paperless-ngx.com/usage/#basic-usage_searching
        """
        async with self.reduce(query=query):
            async for item in self:
                yield item
