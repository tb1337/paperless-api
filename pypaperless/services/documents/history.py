"""Provide `DocumentHistory` related services."""

from typing import TYPE_CHECKING, cast

from pypaperless.const import API_PATH, PaperlessResource
from pypaperless.exceptions import PrimaryKeyRequiredError
from pypaperless.models.documents.history import DocumentHistory
from pypaperless.services.base import ServiceBase

if TYPE_CHECKING:
    from pypaperless import Paperless


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
