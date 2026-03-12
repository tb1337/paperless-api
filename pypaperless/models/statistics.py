"""Provide `Statistics` related models."""

from typing import ClassVar

from pydantic import BaseModel

from pypaperless.const import API_PATH

from .base import PaperlessModel


class StatisticDocumentFileTypeCount(BaseModel):
    """Represent a Paperless statistics file type count."""

    mime_type: str | None = None
    mime_type_count: int | None = None


class Statistic(PaperlessModel):
    """Represent Paperless `Statistic`."""

    _api_path: ClassVar[str] = API_PATH["statistics"]

    documents_total: int | None = None
    documents_inbox: int | None = None
    inbox_tag: int | None = None
    inbox_tags: list[int] | None = None
    document_file_type_counts: list[StatisticDocumentFileTypeCount] | None = None
    character_count: int | None = None
    tag_count: int | None = None
    correspondent_count: int | None = None
    document_type_count: int | None = None
    storage_path_count: int | None = None
    current_asn: int | None = None
