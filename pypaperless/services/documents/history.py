"""Provide `DocumentHistory` related services."""

from pypaperless.const import API_PATH, PaperlessResource
from pypaperless.models.documents.history import DocumentHistory

from .base import DocumentScopedServiceBase


class DocumentHistoryService(DocumentScopedServiceBase):
    """Represent a factory for Paperless `DocumentHistory` models."""

    _api_path = API_PATH["documents_history"]
    _resource = PaperlessResource.DOCUMENTS

    _resource_cls = DocumentHistory

    async def __call__(self, pk: int | None = None) -> list[DocumentHistory]:
        """Request and return the document history entries."""
        doc_pk = self._get_document_pk(pk)
        res = await self._client.request_json("get", self._api_path.format(pk=doc_pk))
        return [
            self._resource_cls.from_data(self._client, {**item, "document": doc_pk}) for item in res
        ]
