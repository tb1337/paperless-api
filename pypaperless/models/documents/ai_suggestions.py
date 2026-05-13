"""Provide `DocumentAISuggestions` related models."""

from typing import ClassVar

from pypaperless.const import EndpointPath
from pypaperless.models.base import PaperlessModel


class DocumentAISuggestions(PaperlessModel):
    """Represent a Paperless `Document`'s AI-generated suggestions."""

    _api_path: ClassVar[str] = EndpointPath.DOCUMENTS_AI_SUGGESTIONS

    id: int | None = None
    title: str | None = None
    correspondents: list[int] | None = None
    suggested_correspondents: list[str] | None = None
    tags: list[int] | None = None
    suggested_tags: list[str] | None = None
    document_types: list[int] | None = None
    suggested_document_types: list[str] | None = None
    storage_paths: list[int] | None = None
    suggested_storage_paths: list[str] | None = None
    dates: list[str] | None = None
