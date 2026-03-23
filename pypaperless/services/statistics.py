"""Provide `Statistic` service."""

from pypaperless.const import API_PATH, PaperlessResource
from pypaperless.models.statistics import Statistic

from .base import ResourceService


class StatisticService(ResourceService):
    """Represent a factory for Paperless `Statistic` models."""

    _api_path = API_PATH["statistics"]
    _resource = PaperlessResource.STATISTICS

    _resource_cls = Statistic

    async def __call__(self) -> Statistic:
        """Fetch document statistics from Paperless.

        Example::

            stats = await paperless.statistics()
            print(f"{stats.documents_total} documents total")

        """
        res = await self._runtime.transport.get(self._api_path)
        return self._resource_cls.from_data(self._runtime, res)
