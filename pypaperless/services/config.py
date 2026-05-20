"""Provide `Config` service."""

from pypaperless.const import EndpointPath
from pypaperless.models.config import Config

from .base import ResourceService


class ConfigService(ResourceService):
    """Represent a factory for Paperless `Config` models."""

    _api_path = EndpointPath.CONFIG

    _resource_cls = Config

    async def __call__(self) -> Config:
        """Fetch the Paperless application configuration.

        Example::

            cfg = await paperless.config()
            print(cfg.user_args)

        """
        api_path = self._resource_cls.format_api_path(pk=1)
        res = await self._runtime.transport.get(api_path)
        return self._resource_cls.from_data(self._runtime, res)
