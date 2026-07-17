"""Provide `DocumentNote` related services."""

from typing import TYPE_CHECKING, Any, cast

from pypaperless.const import EndpointPath, PaperlessResource
from pypaperless.exceptions import (
    DeletionError,
    JsonResponseWithError,
    PrimaryKeyRequiredError,
)
from pypaperless.models.base import DraftLike
from pypaperless.models.documents.notes import DocumentNote, DocumentNoteDraft
from pypaperless.services.mixins import CreatableService, DeletableService

from .base import DocumentScopedServiceBase

if TYPE_CHECKING:
    from pypaperless.models.documents.document import Document
    from pypaperless.runtime import PaperlessRuntime


class DocumentNoteService(
    DocumentScopedServiceBase,
    DeletableService[DocumentNote],
    CreatableService[DocumentNoteDraft],
):
    """Represent a factory for Paperless `DocumentNote` models."""

    _api_path = EndpointPath.DOCUMENTS_NOTES
    _resource = PaperlessResource.DOCUMENTS

    _draft_cls = DocumentNoteDraft
    _resource_cls = DocumentNote

    def __init__(
        self,
        runtime: "PaperlessRuntime",
        document: "Document | None" = None,
    ) -> None:
        """Initialize with an optional attached document instance for cache-first reads."""
        super().__init__(runtime)
        self._document: Document | None = document

    def _get_document_pk(self, pk: int | None = None) -> int:
        """Return the effective document pk from the call-time argument or document instance."""
        resolved = pk or (self._document.id if self._document else None)
        if not resolved:
            message = f"Accessing {type(self).__name__} data without a primary key."
            raise PrimaryKeyRequiredError(message)
        return resolved

    async def __call__(
        self,
        pk: int | None = None,
        *,
        force_request: bool = False,
    ) -> list[DocumentNote]:
        """Return all notes for a document.

        By default the notes already embedded in the parent
        :class:`~pypaperless.models.documents.document.Document` are returned
        directly, without a second API request.  Pass ``force_request=True`` to
        always fetch fresh data from the API and refresh the embedded cache.

        Args:
            pk:            Document primary key.  May be omitted when the service is
                           accessed via a :class:`~pypaperless.models.documents.document.Document`
                           instance (``doc.notes()``).
            force_request: When ``True``, always fetch from the API even if
                           embedded notes are available.

        Example::

            notes = await paperless.documents.notes(42)
            fresh = await doc.notes(force_request=True)

        """
        doc_pk = self._get_document_pk(pk)

        # Return embedded notes from the parent Document when available, avoiding a
        # redundant API request. The cache is kept current by save() and delete().
        if not force_request and self._document is not None and self._document.notes_ is not None:
            return list(self._document.notes_)

        res = await self._runtime.transport.get(self._get_api_path(doc_pk))

        # The notes endpoint does not include the document pk in its response items,
        # so we inject it here. The user dict normalisation is handled by DocumentNote's
        # field_validator.
        notes = [
            self._resource_cls.from_data(
                self._runtime,
                {**item, "document": doc_pk},
            )
            for item in res
        ]
        if self._document is not None:
            self._document.notes_ = notes
        return notes

    def _get_api_path(self, pk: int) -> str:
        """Return the formatted api path."""
        return self._api_path.format(pk=pk)

    def create(self, pk: int | None = None, **kwargs: Any) -> DocumentNoteDraft:
        """Return a new :class:`~pypaperless.models.documents.notes.DocumentNoteDraft` instance.

        Args:
            pk: Document primary key.  May be omitted when the service is
                accessed via a document instance.

        Example::

            draft = paperless.documents.notes.create(42, note="Checked and approved.")
            note_id = await paperless.documents.notes.save(draft)

        """
        kwargs.update({"document": self._get_document_pk(pk)})
        return DocumentNoteDraft.from_data(
            self._runtime,
            data=kwargs,
        )

    async def save(self, draft: DraftLike) -> int:
        """Persist a note draft to Paperless and return the new note id.

        Args:
            draft: A draft instance created by :meth:`create`.

        Example::

            draft = paperless.documents.notes.create(42, note="Approved.")
            note_id = await paperless.documents.notes.save(draft)

        """
        draft.validate_draft()
        kwdict = draft.serialize()
        res = await self._runtime.transport.post(draft.api_path, **kwdict)
        if isinstance(res, dict):
            # Paperless responds with HTTP 200 and an error payload when it
            # cannot save the note (e.g. the search index is locked).
            raise JsonResponseWithError(res)
        new_id = cast("int", max(item.get("id") for item in res))
        if self._document is not None:
            # The POST response is the full updated notes list — keep the cache current.
            self._document.notes_ = [
                self._resource_cls.from_data(self._runtime, {**item, "document": self._document.id})
                for item in res
            ]
        return new_id

    async def delete(
        self,
        note: DocumentNote | int,
        pk: int | None = None,
        *,
        silent_fail: bool = False,
    ) -> None:
        """Delete a document note.

        Raises :exc:`~pypaperless.exceptions.DeletionError` on failure unless
        *silent_fail* is ``True``.

        *note* may be either a
        :class:`~pypaperless.models.documents.notes.DocumentNote` instance **or**
        the integer id of the note to delete.  When an integer is given the
        document primary key must be resolvable — either from the parent
        :class:`~pypaperless.models.documents.document.Document` (when accessed
        via ``doc.notes``) or from the *pk* parameter (standalone use).

        Args:
            note:        The :class:`~pypaperless.models.documents.notes.DocumentNote`
                         instance **or** the integer note id to delete.
            pk:          Document primary key.  May be omitted when the service is
                         accessed via a document instance or when *note* is a
                         :class:`~pypaperless.models.documents.notes.DocumentNote`
                         (whose document pk is embedded in the model).
            silent_fail: When ``True``, swallow :exc:`~pypaperless.exceptions.DeletionError`
                         instead of raising it.

        Example::

            # model-based (existing style)
            notes = await paperless.documents.notes(42)
            await paperless.documents.notes.delete(notes[0])

            # integer shorthand — document context provides the document pk implicitly
            doc = await paperless.documents(42)
            await doc.notes.delete(7)

            # integer shorthand — standalone, document pk passed explicitly
            await paperless.documents.notes.delete(7, pk=42)

        """
        if isinstance(note, int):
            doc_pk = self._get_document_pk(pk)
            note_id: int | None = note
            path = self._get_api_path(doc_pk)
        else:
            note_id = note.id
            path = note.api_path

        params = {"id": note_id}
        try:
            await self._runtime.transport.delete(path, params=params)
        except DeletionError:
            if not silent_fail:
                raise
        else:
            if self._document is not None and self._document.notes_ is not None:
                # Remove the deleted note from the cache directly.
                self._document.notes_ = [n for n in self._document.notes_ if n.id != note_id]
