"""Provide `DocumentChat` related models."""

from typing import ClassVar

from pypaperless.const import EndpointPath, PaperlessResource
from pypaperless.models.base import PaperlessModel


class DocumentChat(PaperlessModel):
    """Represent a Paperless `Document` chat response."""

    _api_path: ClassVar[str] = EndpointPath.DOCUMENTS_CHAT
    _resource: ClassVar[PaperlessResource] = PaperlessResource.DOCUMENTS

    q: str | None = None
    document_id: int | None = None
