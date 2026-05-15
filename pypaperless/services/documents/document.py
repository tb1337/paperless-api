"""Provide `Document` related services."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Self, Unpack

from pypaperless.const import EndpointPath, PaperlessResource
from pypaperless.exceptions import AsnRequestError, SendEmailError
from pypaperless.models.documents.document import (
    Document,
    DocumentDraft,
    DocumentMeta,
    DocumentSuggestions,
)
from pypaperless.models.filters import DocumentFilters
from pypaperless.services import mixins
from pypaperless.services.base import ResourceService

from .ai_suggestions import DocumentAISuggestionsService
from .bulk_edit import DocumentBulkEditService
from .chat import DocumentChatService
from .files import (
    DocumentFileDownloadService,
    DocumentFilePreviewService,
    DocumentFileThumbnailService,
)
from .history import DocumentHistoryService
from .notes import DocumentNoteService
from .share_links import DocumentShareLinkService
from .versions import DocumentRootService, DocumentVersionService

if TYPE_CHECKING:
    from pypaperless.runtime import PaperlessRuntime


class DocumentSuggestionsService(ResourceService):
    """Represent a factory for Paperless `DocumentSuggestions` models."""

    _api_path = EndpointPath.DOCUMENTS_SUGGESTIONS
    _resource = PaperlessResource.DOCUMENTS

    _resource_cls = DocumentSuggestions

    async def __call__(self, pk: int) -> DocumentSuggestions:
        """Request exactly one resource item."""
        api_path = self._resource_cls.format_api_path(pk=pk)
        data = await self._runtime.transport.get(api_path)
        data["id"] = pk

        return self._resource_cls.from_data(self._runtime, data)


class DocumentMetaService(ResourceService, mixins.CallableService[DocumentMeta]):
    """Represent a factory for Paperless `DocumentMeta` models."""

    _api_path = EndpointPath.DOCUMENTS_META
    _resource = PaperlessResource.DOCUMENTS

    _resource_cls = DocumentMeta


class DocumentService(
    ResourceService,
    mixins.SecurableService,
    mixins.CallableService[Document],
    mixins.CreatableService[DocumentDraft],
    mixins.IterableService[Document],
    mixins.UpdatableService[Document],
    mixins.DeletableService[Document],
):
    """Represent a factory for Paperless `Document` models."""

    _api_path = EndpointPath.DOCUMENTS
    _resource = PaperlessResource.DOCUMENTS

    _draft_cls = DocumentDraft
    _resource_cls = Document

    @asynccontextmanager
    async def filter(self, **kwargs: Unpack[DocumentFilters]) -> AsyncGenerator[Self]:
        """Iterate documents with server-side filters.

        See :class:`~pypaperless.models.filters.DocumentFilters` for all available keys.

        Example::

            async with paperless.documents.filter(
                title__icontains="invoice",
                tag__id__all=[3, 7],
            ) as filtered:
                async for doc in filtered:
                    print(doc.title)

        """
        async with self._store_filters(**kwargs) as ctx:
            yield ctx

    def __init__(self, runtime: "PaperlessRuntime") -> None:
        """Initialize a `DocumentService` instance."""
        super().__init__(runtime)

        self._ai_suggestions = DocumentAISuggestionsService(runtime)
        self._bulk_edit = DocumentBulkEditService(runtime)
        self._chat = DocumentChatService(runtime)
        self._download = DocumentFileDownloadService(runtime)
        self._history = DocumentHistoryService(runtime)
        self._meta = DocumentMetaService(runtime)
        self._notes = DocumentNoteService(runtime)
        self._preview = DocumentFilePreviewService(runtime)
        self._share_links = DocumentShareLinkService(runtime)
        self._suggestions = DocumentSuggestionsService(runtime)
        self._thumbnail = DocumentFileThumbnailService(runtime)
        self._root = DocumentRootService(runtime)
        self._versions = DocumentVersionService(runtime)

    @property
    def ai_suggestions(self) -> DocumentAISuggestionsService:
        """Return the ``DocumentAISuggestionsService`` sub-service.

        Example::

            result = await paperless.documents.ai_suggestions(42)
            print(result.title, result.suggested_tags)

        """
        return self._ai_suggestions

    @property
    def bulk_edit(self) -> DocumentBulkEditService:
        """Return the ``DocumentBulkEditService`` sub-service.

        Example::

            await paperless.documents.bulk_edit.set_correspondent([1, 2], 5)

        """
        return self._bulk_edit

    @property
    def chat(self) -> DocumentChatService:
        """Return the ``DocumentChatService`` sub-service.

        Example::

            response = await paperless.documents.chat("What is this invoice about?", 42)
            print(response.q)

        """
        return self._chat

    @property
    def download(self) -> DocumentFileDownloadService:
        """Return the ``DocumentFileDownloadService`` sub-service.

        Example::

            result = await paperless.documents.download(42)
            with open(result.disposition_filename, "wb") as f:
                f.write(result.content)

        """
        return self._download

    @property
    def history(self) -> DocumentHistoryService:
        """Return the ``DocumentHistoryService`` sub-service.

        Example::

            # fetch history for a document by pk
            entries = await paperless.documents.history(42)

            # or via an already-fetched document
            doc = await paperless.documents(42)
            entries = await doc.history()

        """
        return self._history

    @property
    def metadata(self) -> DocumentMetaService:
        """Return the ``DocumentMetaService`` sub-service.

        Example::

            meta = await paperless.documents.metadata(42)
            print(meta.media_filename)

        """
        return self._meta

    @property
    def notes(self) -> DocumentNoteService:
        """Return the ``DocumentNoteService`` sub-service.

        Example::

            # fetch notes by document pk
            notes = await paperless.documents.notes(42)

            # or via an already-fetched document
            doc = await paperless.documents(42)
            notes = await doc.notes()

        """
        return self._notes

    @property
    def share_links(self) -> DocumentShareLinkService:
        """Return the ``DocumentShareLinkService`` sub-service.

        Example::

            # fetch share links by document pk
            links = await paperless.documents.share_links(42)

            # or via an already-fetched document
            doc = await paperless.documents(42)
            links = await doc.share_links()

        """
        return self._share_links

    @property
    def preview(self) -> DocumentFilePreviewService:
        """Return the ``DocumentFilePreviewService`` sub-service.

        Example::

            result = await paperless.documents.preview(42)

        """
        return self._preview

    @property
    def suggestions(self) -> DocumentSuggestionsService:
        """Return the ``DocumentSuggestionsService`` sub-service.

        Example::

            suggestions = await paperless.documents.suggestions(42)
            print(suggestions.correspondents)

        """
        return self._suggestions

    @property
    def thumbnail(self) -> DocumentFileThumbnailService:
        """Return the ``DocumentFileThumbnailService`` sub-service.

        Example::

            result = await paperless.documents.thumbnail(42)

        """
        return self._thumbnail

    @property
    def root(self) -> DocumentRootService:
        """Return the ``DocumentRootService`` sub-service.

        Example::

            result = await paperless.documents.root(42)
            print(result.root_id)

        """
        return self._root

    @property
    def versions(self) -> DocumentVersionService:
        """Return the ``DocumentVersionService`` sub-service.

        Example::

            await paperless.documents.versions.upload(file, pk=42)
            result = await paperless.documents.versions.update(1, version_label="v2", pk=42)
            await paperless.documents.versions.delete(1, pk=42)

        """
        return self._versions

    async def get_next_asn(self) -> int:
        """Request the next available archive serial number from Paperless.

        Example::

            asn = await paperless.documents.get_next_asn()
            draft.archive_serial_number = asn

        """
        res = await self._runtime.transport.request_raw("get", EndpointPath.DOCUMENTS_NEXT_ASN)
        try:
            res.raise_for_status()
            return int(res.text)
        except Exception as exc:
            raise AsnRequestError from exc

    async def more_like(self, pk: int) -> AsyncGenerator[Document]:
        """Iterate documents similar to the given document.

        Uses the full-text index to find semantically related documents.
        Shortcut for :meth:`filter` with ``more_like_id``.

        Args:
            pk: Primary key of the reference document.

        Example::

            async for doc in paperless.documents.more_like(42):
                print(doc.title)

        """
        async with self.filter(more_like_id=pk):
            async for item in self:
                yield item

    async def search(
        self, query: str | None = None, custom_field_query: str | None = None
    ) -> AsyncGenerator[Document]:
        """Iterate documents matching a full-text search and/or custom field query.

        When neither argument is provided, all documents are returned.  This is
        a shortcut for :meth:`filter` with ``query`` / ``custom_field_query``.

        Args:
            query:              Whoosh-style full-text query string, or a
                                :class:`~pypaperless.builders.search.SearchQuery`
                                builder object cast to ``str``.
            custom_field_query: JSON-encoded custom field query, typically produced
                                by a :class:`~pypaperless.builders.custom_fields.CustomFieldQuery`
                                builder object.

        Example::

            async for doc in paperless.documents.search("invoice"):
                print(doc.title)

            # with a custom field filter
            from pypaperless.builders.custom_fields import CustomFieldQuery
            q = CustomFieldQuery("Status", "exact", "open")
            async for doc in paperless.documents.search(custom_field_query=str(q)):
                print(doc.title)

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
        """Email one or more documents to recipients as attachments.

        Args:
            documents:           Single document pk or a list of pks to send.
            addresses:           Comma-separated list of recipient e-mail addresses.
            subject:             E-mail subject line.
            message:             E-mail body text.
            use_archive_version: When ``True`` (default), the archived PDF is
                                 attached instead of the original file.

        Example::

            await paperless.documents.email(
                [23, 42],
                addresses="alice@example.com, bob@example.com",
                subject="Your documents",
                message="Please find the attached files.",
            )

        """
        data = {
            "documents": [documents] if isinstance(documents, int) else documents,
            "addresses": addresses,
            "subject": subject,
            "message": message,
            "use_archive_version": use_archive_version,
        }
        try:
            await self._runtime.transport.post(EndpointPath.DOCUMENTS_EMAIL, json=data)
        except Exception as exc:
            raise SendEmailError from exc
