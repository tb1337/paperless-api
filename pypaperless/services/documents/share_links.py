"""Provide document-scoped `ShareLink` services."""

from pypaperless.const import API_PATH, PaperlessResource
from pypaperless.models.share_links import ShareLink

from .base import DocumentScopedServiceBase


class DocumentShareLinkService(DocumentScopedServiceBase):
    """Represent a factory for document-scoped Paperless `ShareLink` models."""

    _api_path = API_PATH["documents_share_links"]
    _resource = PaperlessResource.DOCUMENTS

    _resource_cls = ShareLink

    async def __call__(self, pk: int | None = None) -> list[ShareLink]:
        """Request and return the document's `ShareLink` list."""
        doc_pk = self._get_document_pk(pk)
        res = await self._client.request_json("get", self._api_path.format(pk=doc_pk))
        return [self._resource_cls.from_data(self._client, item) for item in res]
