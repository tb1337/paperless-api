"""Provide `DocumentChat` related models."""

from typing import ClassVar

from pypaperless.const import EndpointPath
from pypaperless.models.base import PaperlessModel


class DocumentChat(PaperlessModel):
    """Represent a Paperless `Document` chat response."""

    _api_path: ClassVar[str] = EndpointPath.DOCUMENTS_CHAT

    q: str | None = None
    document_id: int | None = None
