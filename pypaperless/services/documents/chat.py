"""Provide `DocumentChat` service."""

from pypaperless.const import EndpointPath
from pypaperless.models.documents.chat import DocumentChat
from pypaperless.services.base import PaperlessService


class DocumentChatService(PaperlessService):
    """Perform an LLM-powered chat query against Paperless documents."""

    _api_path = EndpointPath.DOCUMENTS_CHAT

    async def __call__(self, q: str, document_id: int | None = None) -> DocumentChat:
        """Send a chat query to Paperless and return the response.

        Args:
            q:           The question or query string.
            document_id: Optional document primary key to scope the query.

        Example::

            response = await paperless.documents.chat("What is this invoice about?", 42)
            print(response.q)

        """
        payload: dict[str, object] = {"q": q}
        if document_id is not None:
            payload["document_id"] = document_id
        data = await self._runtime.transport.post(self._api_path, json=payload)
        return DocumentChat.from_data(self._runtime, data)
