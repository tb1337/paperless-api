"""Provide `DocumentNote` related services."""

from typing import Any, cast

from pypaperless.const import API_PATH, PaperlessResource
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
