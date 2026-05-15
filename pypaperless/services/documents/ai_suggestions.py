"""Provide `DocumentAISuggestions` service."""

from pypaperless.const import EndpointPath, PaperlessResource
from pypaperless.models.documents.ai_suggestions import DocumentAISuggestions

from .base import DocumentScopedServiceBase


class DocumentAISuggestionsService(DocumentScopedServiceBase):
    """Represent a factory for Paperless `DocumentAISuggestions` models."""

    _api_path = EndpointPath.DOCUMENTS_AI_SUGGESTIONS
    _resource = PaperlessResource.DOCUMENTS

    _resource_cls = DocumentAISuggestions

    async def __call__(self, pk: int | None = None) -> DocumentAISuggestions:
        """Return AI-generated suggestions for a document.

        Args:
            pk: Document primary key.  May be omitted when the service is
                accessed via a :class:`~pypaperless.models.documents.document.Document`
                instance (``doc.ai_suggestions()``).

        Example::

            result = await paperless.documents.ai_suggestions(42)
            print(result.title, result.suggested_tags)

        """
        doc_pk = self._get_document_pk(pk)
        api_path = self._api_path.format(pk=doc_pk)
        data = await self._runtime.transport.get(api_path)
        data["id"] = doc_pk
        return self._resource_cls.from_data(self._runtime, data)
