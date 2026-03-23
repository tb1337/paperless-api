"""Provide `DocumentNote` related services."""

from typing import Any, cast

from pypaperless.const import API_PATH, PaperlessResource
from pypaperless.exceptions import DeletionError
from pypaperless.models.documents.notes import DocumentNote, DocumentNoteDraft

from .base import DocumentScopedServiceBase


class DocumentNoteService(DocumentScopedServiceBase):
    """Represent a factory for Paperless `DocumentNote` models."""

    _api_path = API_PATH["documents_notes"]
    _resource = PaperlessResource.DOCUMENTS

    _resource_cls = DocumentNote

    async def __call__(
        self,
        pk: int | None = None,
    ) -> list[DocumentNote]:
        """Return all notes for a document.

        Args:
            pk: Document primary key.  May be omitted when the service is
                accessed via a :class:`~pypaperless.models.documents.document.Document`
                instance (``doc.notes()``).

        Example::

            notes = await paperless.documents.notes(42)
            for note in notes:
                print(note.note)

        """
        doc_pk = self._get_document_pk(pk)
        res = await self._client.transport.get(self._get_api_path(doc_pk))

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
            note_id, doc_id = await paperless.documents.notes.save(draft)

        """
        kwargs.update({"document": self._get_document_pk(pk)})
        return DocumentNoteDraft.from_data(
            self._client,
            data=kwargs,
        )

    async def save(self, draft: DocumentNoteDraft) -> tuple[int, int]:
        """Persist a note draft to Paperless.

        Returns a ``(note_id, document_id)`` tuple.

        Args:
            draft: A draft instance created by :meth:`create`.

        Example::

            draft = paperless.documents.notes.create(42, note="Approved.")
            note_id, doc_id = await paperless.documents.notes.save(draft)

        """
        draft.validate_draft()
        kwdict = draft.serialize()
        res = await self._client.transport.post(draft.api_path, **kwdict)
        return (
            cast("int", max(item.get("id") for item in res)),
            cast("int", kwdict["json"]["document"]),
        )

    async def delete(self, note: DocumentNote, *, silent_fail: bool = False) -> None:
        """Delete a document note.

        Raises :exc:`~pypaperless.exceptions.DeletionError` on failure unless
        *silent_fail* is ``True``.

        Args:
            note:        The :class:`~pypaperless.models.documents.notes.DocumentNote`
                         instance to delete.
            silent_fail: When ``True``, swallow :exc:`~pypaperless.exceptions.DeletionError`
                         instead of raising it.

        Example::

            notes = await paperless.documents.notes(42)
            if notes:
                await paperless.documents.notes.delete(notes[0])

        """
        params = {
            "id": note.id,
        }
        try:
            await self._client.transport.delete(note.api_path, params=params)
        except DeletionError:
            if not silent_fail:
                raise
