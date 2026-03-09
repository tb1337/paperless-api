"""Provide `Statistics` related models and services."""

from typing import ClassVar

from pypaperless.const import API_PATH, PaperlessResource

from .base import ServiceBase, PaperlessModel
from .common import StatisticDocumentFileTypeCount


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


class StatisticService(ServiceBase):
    """Represent a factory for Paperless `Statistic` models."""

    _api_path = API_PATH["statistics"]
    _resource = PaperlessResource.STATISTICS

    _resource_cls = Statistic

    async def __call__(self) -> Statistic:
        """Request the `Statistic` model data."""
        res = await self._client.request_json("get", self._api_path)
        return self._resource_cls.create_with_data(self._client, res, fetched=True)
