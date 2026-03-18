"""Provide `Document` related services."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Any, ClassVar, Self, Unpack, cast

from pypaperless.const import API_PATH, PaperlessResource
from pypaperless.exceptions import AsnRequestError, PrimaryKeyRequiredError, SendEmailError
from pypaperless.models.documents import (
    Document,
    DocumentDraft,
    DocumentHistory,
    DocumentMeta,
    DocumentNote,
    DocumentNoteDraft,
    DocumentSuggestions,
    DownloadedDocument,
    FileRetrieveMode,
)
from pypaperless.models.filters import DocumentFilters
from pypaperless.models.share_links import ShareLink

from . import mixins
from .base import ServiceBase

if TYPE_CHECKING:
    from pypaperless import Paperless


class DocumentSuggestionsService(ServiceBase):
    """Represent a factory for Paperless `DocumentSuggestions` models."""

    _api_path = API_PATH["documents_suggestions"]
    _resource = PaperlessResource.DOCUMENTS

    _resource_cls = DocumentSuggestions

    async def __call__(self, pk: int) -> DocumentSuggestions:
        """Request exactly one resource item."""
        api_path = self._resource_cls.format_api_path(pk=pk)
        data = await self._client.request_json("get", api_path)
        data["id"] = pk

        return self._resource_cls.from_data(self._client, data)


class DocumentSubServiceBase(ServiceBase):
    """Represent a factory for Paperless `DownloadedDocument` models."""

    _api_path = API_PATH["documents_suggestions"]
    _resource = PaperlessResource.DOCUMENTS
    _mode: ClassVar[FileRetrieveMode]

    _resource_cls = DownloadedDocument

    async def __call__(self, pk: int, *, original: bool = False) -> DownloadedDocument:
        """Request exactly one resource item."""
        params = {
            "original": "true" if original else "false",
        }

        res = await self._client.request("get", self._api_path.format(pk=pk), params=params)

        data: dict[str, Any] = {
            "id": pk,
            "mode": self._mode,
            "original": original,
            "content": res.content,
            "content_type": res.headers.get("content-type"),
        }

        content_disposition = res.headers.get("content-disposition")
        if content_disposition is not None:
            parts = content_disposition.split(";")
            data["disposition_type"] = parts[0].strip()
            for part in parts[1:]:
                stripped = part.strip()
                if stripped.startswith("filename="):
                    data["disposition_filename"] = stripped.split("=", 1)[1].strip('"')

        return self._resource_cls.from_data(self._client, data)


class DocumentFileDownloadService(DocumentSubServiceBase):
    """Represent a factory for Paperless `DownloadedDocument` models."""

    _api_path = API_PATH["documents_download"]
    _mode = FileRetrieveMode.DOWNLOAD


class DocumentFilePreviewService(DocumentSubServiceBase):
    """Represent a factory for Paperless `DownloadedDocument` models."""

    _api_path = API_PATH["documents_preview"]
    _mode = FileRetrieveMode.PREVIEW


class DocumentFileThumbnailService(DocumentSubServiceBase):
    """Represent a factory for Paperless `DownloadedDocument` models."""

    _api_path = API_PATH["documents_thumbnail"]
    _mode = FileRetrieveMode.THUMBNAIL


class DocumentHistoryService(ServiceBase):
    """Represent a factory for Paperless `DocumentHistory` models."""

    _api_path = API_PATH["documents_history"]
    _resource = PaperlessResource.DOCUMENTS

    _resource_cls = DocumentHistory

    def __init__(self, client: "Paperless", attached_to: int | None = None) -> None:
        """Initialize a `DocumentHistoryService` instance."""
        super().__init__(client)

        self._attached_to = attached_to

    async def __call__(self, pk: int | None = None) -> list[DocumentHistory]:
        """Request and return the document history entries."""
        doc_pk = self._get_document_pk(pk)
        res = await self._client.request_json("get", self._api_path.format(pk=doc_pk))
        return [
            self._resource_cls.from_data(self._client, {**item, "document": doc_pk}) for item in res
        ]

    def _get_document_pk(self, pk: int | None = None) -> int:
        """Return the attached document pk, or the parameter."""
        if not any((self._attached_to, pk)):
            message = f"Accessing {type(self).__name__} data without a primary key."
            raise PrimaryKeyRequiredError(message)
        return cast("int", self._attached_to or pk)


class DocumentShareLinkService(ServiceBase):
    """Represent a factory for document-scoped Paperless `ShareLink` models."""

    _api_path = API_PATH["documents_share_links"]
    _resource = PaperlessResource.DOCUMENTS

    _resource_cls = ShareLink

    def __init__(self, client: "Paperless", attached_to: int | None = None) -> None:
        """Initialize a `DocumentShareLinkService` instance."""
        super().__init__(client)

        self._attached_to = attached_to

    async def __call__(self, pk: int | None = None) -> list[ShareLink]:
        """Request and return the document's `ShareLink` list."""
        doc_pk = self._get_document_pk(pk)
        res = await self._client.request_json("get", self._api_path.format(pk=doc_pk))
        return [self._resource_cls.from_data(self._client, item) for item in res]

    def _get_document_pk(self, pk: int | None = None) -> int:
        """Return the attached document pk, or the parameter."""
        if not any((self._attached_to, pk)):
            message = f"Accessing {type(self).__name__} data without a primary key."
            raise PrimaryKeyRequiredError(message)
        return cast("int", self._attached_to or pk)


class DocumentMetaService(ServiceBase, mixins.CallableMixin[DocumentMeta]):
    """Represent a factory for Paperless `DocumentMeta` models."""

    _api_path = API_PATH["documents_meta"]
    _resource = PaperlessResource.DOCUMENTS

    _resource_cls = DocumentMeta


class DocumentNoteService(ServiceBase):
    """Represent a factory for Paperless `DocumentNote` models."""

    _api_path = API_PATH["documents_notes"]
    _resource = PaperlessResource.DOCUMENTS

    _resource_cls = DocumentNote

    def __init__(self, client: "Paperless", attached_to: int | None = None) -> None:
        """Initialize a `DocumentNoteService` instance."""
        super().__init__(client)

        self._attached_to = attached_to

    async def __call__(
        self,
        pk: int | None = None,
    ) -> list[DocumentNote]:
        """Request and return the documents `DocumentNote` list."""
        doc_pk = self._get_document_pk(pk)
        res = await self._client.request_json("get", self._get_api_path(doc_pk))

        # We have to transform data here slightly.
        # There are two major differences in the data depending on which endpoint is requested.
        # url: documents/{:pk}/ ->
        #       .document -> int
        #       .user -> int
        # url: documents/{:pk}/notes/ ->
        #       .document -> does not exist (so we add it here)
        #       .user -> dict(id=int, username=str, first_name=str, last_name=str)
        return [
            self._resource_cls.from_data(
                self._client,
                {
                    **item,
                    "document": doc_pk,
                    "user": item["user"]["id"]
                    if self._client.host_api_version >= 8
                    else item["user"],
                },
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

    def create(self, pk: int | None = None, **kwargs: Any) -> DocumentNoteDraft:
        """Return a fresh and empty `DocumentNoteDraft` instance.

        Example:
        -------
        ```python
        draft = paperless.documents.notes.create(...)
        # do something
        ```

        """
        kwargs.update({"document": self._get_document_pk(pk)})
        return DocumentNoteDraft.from_data(
            self._client,
            data=kwargs,
        )

    async def save(self, draft: DocumentNoteDraft) -> tuple[int, int]:
        """Create a new `DocumentNote` in Paperless.

        Return a tuple of (note_id, document_id).
        """
        draft.validate_draft()
        kwdict = draft.serialize()
        res = await self._client.request_json("post", draft.api_path, **kwdict)
        return (
            cast("int", max(item.get("id") for item in res)),
            cast("int", kwdict["json"]["document"]),
        )

    async def delete(self, note: DocumentNote) -> bool:
        """Delete a document note.

        Return `True` when deletion was successful, `False` otherwise.
        """
        params = {
            "id": note.id,
        }
        res = await self._client.request("delete", note.api_path, params=params)
        return res.status_code in {200, 204}


class DocumentService(
    ServiceBase,
    mixins.SecurableMixin,
    mixins.CallableMixin[Document],
    mixins.DraftableMixin[DocumentDraft],
    mixins.IterableMixin[Document],
    mixins.UpdatableMixin[Document],
    mixins.DeletableMixin[Document],
):
    """Represent a factory for Paperless `Document` models."""

    _api_path = API_PATH["documents"]
    _resource = PaperlessResource.DOCUMENTS

    _draft_cls = DocumentDraft
    _resource_cls = Document

    @asynccontextmanager
    async def filter(self, **kwargs: Unpack[DocumentFilters]) -> AsyncGenerator[Self]:
        """Iterate with server-side filters.

        See :class:`~pypaperless.models.filters.DocumentFilters` for available keys.
        """
        async with self._store_filters(**kwargs) as ctx:
            yield ctx

    def __init__(self, client: "Paperless") -> None:
        """Initialize a `DocumentService` instance."""
        super().__init__(client)

        self._download = DocumentFileDownloadService(client)
        self._history = DocumentHistoryService(client)
        self._meta = DocumentMetaService(client)
        self._notes = DocumentNoteService(client)
        self._preview = DocumentFilePreviewService(client)
        self._share_links = DocumentShareLinkService(client)
        self._suggestions = DocumentSuggestionsService(client)
        self._thumbnail = DocumentFileThumbnailService(client)

    @property
    def download(self) -> DocumentFileDownloadService:
        """Download the contents of an archived file.

        Example:
        -------
        ```python
        download = await paperless.documents.download(42)
        ```

        """
        return self._download

    @property
    def history(self) -> DocumentHistoryService:
        """Return the attached `DocumentHistoryService` instance.

        Example:
        -------
        ```python
        # request history of a document directly...
        entries = await paperless.documents.history(42)

        # ... or by using an already fetched document
        doc = await paperless.documents(42)
        entries = await doc.history()
        ```

        """
        return self._history

    @property
    def metadata(self) -> DocumentMetaService:
        """Return the attached `DocumentMetaService` instance.

        Example:
        -------
        ```python
        metadata = await paperless.documents.metadata(42)
        ```

        """
        return self._meta

    @property
    def notes(self) -> DocumentNoteService:
        """Return the attached `DocumentNoteService` instance.

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
    def share_links(self) -> DocumentShareLinkService:
        """Return the attached `DocumentShareLinkService` instance.

        Example:
        -------
        ```python
        # request document share links directly...
        links = await paperless.documents.share_links(42)

        # ... or by using an already fetched document
        doc = await paperless.documents(42)
        links = await doc.share_links()
        ```

        """
        return self._share_links

    @property
    def preview(self) -> DocumentFilePreviewService:
        """Preview the contents of an archived file.

        Example:
        -------
        ```python
        download = await paperless.documents.preview(42)
        ```

        """
        return self._preview

    @property
    def suggestions(self) -> DocumentSuggestionsService:
        """Return the attached `DocumentSuggestionsService` instance.

        Example:
        -------
        ```python
        suggestions = await paperless.documents.suggestions(42)
        ```

        """
        return self._suggestions

    @property
    def thumbnail(self) -> DocumentFileThumbnailService:
        """Download the contents of a thumbnail file.

        Example:
        -------
        ```python
        download = await paperless.documents.thumbnail(42)
        ```

        """
        return self._thumbnail

    async def get_next_asn(self) -> int:
        """Request the next archive serial number from DRF."""
        res = await self._client.request("get", API_PATH["documents_next_asn"])
        try:
            res.raise_for_status()
            return int(res.text)
        except Exception as exc:
            raise AsnRequestError from exc

    async def more_like(self, pk: int) -> AsyncGenerator[Document]:
        """Lookup documents similar to the given document pk.

        Shortcut function. Same behaviour is possible using `filter()`.

        Documentation: https://docs.paperless-ngx.com/api/#searching-for-documents
        """
        async with self.filter(more_like_id=pk):
            async for item in self:
                yield item

    async def search(
        self, query: str | None = None, custom_field_query: str | None = None
    ) -> AsyncGenerator[Document]:
        """Lookup documents by a search query and/or custom_field_query.

        If none of both are provided, all documents are returned.

        Shortcut function. Same behaviour is possible using `filter()`.

        Documentation: https://docs.paperless-ngx.com/usage/#basic-usage_searching
        """
        filters: DocumentFilters = {}
        if query is not None:
            filters["query"] = query
        if custom_field_query is not None:
            filters["custom_field_query"] = custom_field_query

        async with self.filter(**filters):
            async for item in self:
                yield item

    async def email(
        self,
        documents: int | list[int],
        *,
        addresses: str,
        subject: str,
        message: str,
        use_archive_version: bool = True,
    ) -> None:
        """Email documents to one or more recipients as an attachment.

        Example:
        -------
        ```python
        # email document directly...
        await paperless.documents.email(
            [23, 42],
            addresses="example@example.com, another@example.com",
            subject="Subject",
            message="Message"
        )
        ```

        """
        data = {
            "documents": [documents] if isinstance(documents, int) else documents,
            "addresses": addresses,
            "subject": subject,
            "message": message,
            "use_archive_version": use_archive_version,
        }
        res = await self._client.request("post", API_PATH["documents_email"], json=data)
        try:
            res.raise_for_status()
        except Exception as exc:
            raise SendEmailError from exc
