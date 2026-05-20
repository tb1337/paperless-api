"""Provide document-scoped `ShareLink` services."""

from pypaperless.const import EndpointPath
from pypaperless.models.share_links import ShareLink

from .base import DocumentScopedServiceBase


class DocumentShareLinkService(DocumentScopedServiceBase):
    """Represent a factory for document-scoped Paperless `ShareLink` models."""

    _api_path = EndpointPath.DOCUMENTS_SHARE_LINKS

    _resource_cls = ShareLink

    async def __call__(self, pk: int | None = None) -> list[ShareLink]:
        """Return all share links for a document.

        Args:
            pk: Document primary key.  May be omitted when the service is
                accessed via a :class:`~pypaperless.models.documents.document.Document`
                instance (``doc.share_links()``).

        Example::

            links = await paperless.documents.share_links(42)
            for link in links:
                print(link.slug)

        """
        doc_pk = self._get_document_pk(pk)
        res = await self._runtime.transport.get(self._api_path.format(pk=doc_pk))
        return [self._resource_cls.from_data(self._runtime, item) for item in res]
