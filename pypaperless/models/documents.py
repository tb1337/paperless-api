"""Provide `Document` related models and helpers."""

import datetime
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, cast, final

from pypaperless.const import API_PATH
from pypaperless.errors import PrimaryKeyRequired

from .base import HelperBase, PaperlessModel
from .custom_fields import CustomFieldValueType
from .mixins import helpers, models

if TYPE_CHECKING:
    from pypaperless import Paperless


@final
@dataclass(init=False)
class Document(
    PaperlessModel,
    models.PermissionFieldsMixin,
    models.UpdatableMixin,
    models.DeletableMixin,
):  # pylint: disable=too-many-instance-attributes, too-many-ancestors
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
    archive_serial_number: int | None = None
    original_file_name: str | None = None
    archived_file_name: str | None = None
    is_shared_by_requester: bool | None = None
    custom_fields: list[CustomFieldValueType] | None = None

    def __init__(self, api: "Paperless", data: dict[str, Any]):
        """Initialize a `Document` instance."""
        super().__init__(api, data)

        self._api_path = self._api_path.format(pk=data.get("id"))
        self.notes = DocumentNoteHelper(api, data.get("id"))

    async def get_metadata(self) -> "DocumentMeta":
        """Request and return the documents `DocumentMeta` class."""
        item = await self._api.documents.metadata(cast(int, self.id))
        return item


@final
@dataclass(init=False)
class DocumentDraft(
    PaperlessModel,
    models.CreatableMixin,
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
@dataclass(init=False)
class DocumentNote(PaperlessModel):
    """Represent a Paperless `DocumentNote`."""

    _api_path = API_PATH["documents_notes"]

    id: int | None = None
    note: str | None = None
    created: datetime.datetime | None = None
    document: int | None = None
    user: int | None = None

    def __init__(self, api: "Paperless", data: dict[str, Any]):
        """Initialize a `DocumentNote` instance."""
        super().__init__(api, data)

        self._api_path = self._api_path.format(pk=data.get("document"))

    async def delete(self) -> bool:
        """Delete a `resource item` from DRF. There is no point of return.

        Return `True` when deletion was successful, `False` otherwise.

        Example:
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
        async with self._api.generate_request("delete", self._api_path, params=params) as res:
            success = res.status == 204

        return success


@final
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

    def __init__(self, api: "Paperless", data: dict[str, Any]):
        """Initialize a `DocumentNote` instance."""
        super().__init__(api, data)

        self._api_path = self._api_path.format(pk=data.get("document"))


@final
@dataclass(kw_only=True)
class DocumentMetadataType:
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

    def __init__(self, api: "Paperless", data: dict[str, Any]):
        """Initialize a `DocumentMeta` instance."""
        super().__init__(api, data)

        self._api_path = self._api_path.format(pk=data.get("id"))


@final
class DocumentMetaHelper(  # pylint: disable=too-few-public-methods
    HelperBase[DocumentMeta],
    helpers.CallableMixin[DocumentMeta],
):
    """Represent a factory for Paperless `DocumentMeta` models."""

    _api_path = API_PATH["documents_meta"]

    _resource = DocumentMeta


@final
class DocumentNoteHelper(HelperBase[DocumentNote]):  # pylint: disable=too-few-public-methods
    """Represent a factory for Paperless `DocumentNote` models."""

    _api_path = API_PATH["documents_notes"]

    _resource = DocumentNote

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
            self._resource.create_with_data(
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
            raise PrimaryKeyRequired(f"Accessing {type(self).__name__} data without a primary key.")
        return cast(int, self._attached_to or pk)

    def _get_api_path(self, pk: int) -> str:
        """Return the formatted api path."""
        return self._api_path.format(pk=pk)

    def draft(self, pk: int | None = None, **kwargs: Any) -> DocumentNoteDraft:
        """Return a fresh and empty `DocumentNoteDraft` instance.

        Example:
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


@final
class DocumentHelper(  # pylint: disable=too-many-ancestors
    HelperBase[Document],
    helpers.CallableMixin[Document],
    helpers.DraftableMixin[DocumentDraft],
    helpers.IterableMixin[Document],
):
    """Represent a factory for Paperless `Document` models."""

    _api_path = API_PATH["documents"]

    _draft = DocumentDraft
    _resource = Document

    def __init__(self, api: "Paperless") -> None:
        """Initialize a `DocumentHelper` instance."""
        super().__init__(api)

        self._meta = DocumentMetaHelper(api)
        self._notes = DocumentNoteHelper(api)

    @property
    def metadata(self) -> DocumentMetaHelper:
        """Return the attached `DocumentMetaHelper` instance.

        Example:
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
        ```python
        # request document notes directly...
        notes = await paperless.documents.notes(42)

        # ... or by using an already fetched document
        doc = await paperless.documents(42)
        notes = await doc.notes()
        ```
        """
        return self._notes
