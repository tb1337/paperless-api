"""Provide `Statistic` service."""

from pypaperless.const import API_PATH, PaperlessResource
from pypaperless.models.statistics import Statistic

from .base import ServiceBase


class StatisticService(ServiceBase):
    """Represent a factory for Paperless `Statistic` models."""

    _api_path = API_PATH["statistics"]
    _resource = PaperlessResource.STATISTICS

    _resource_cls = Statistic

    async def __call__(self) -> Statistic:
        """Request the `Statistic` model data."""
        res = await self._client.request_json("get", self._api_path)
        return self._resource_cls.from_data(self._client, res)
