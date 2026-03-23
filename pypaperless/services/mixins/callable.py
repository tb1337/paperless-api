"""CallableService for PyPaperless services."""

from typing import Any

from pypaperless.models.base import ResourceT
from pypaperless.services.base import ResourceServiceProtocol


class CallableService(ResourceServiceProtocol[ResourceT]):
    """Provide methods for calling a specific resource item."""

    async def __call__(
        self,
        pk: int,
        *,
        lazy: bool = False,
    ) -> ResourceT:
        """Request exactly one resource item by primary key.

        Args:
            pk:   Primary key of the resource item to retrieve.
            lazy: When ``True``, return a model instance without hitting the
                  API — only the ``id`` field is populated.

        Example::

            # fetch a document from the API
            document = await paperless.documents(42)

            # initialise a stub without network access
            document = await paperless.documents(42, lazy=True)

        """
        if lazy:
            return self._resource_cls.from_data(self._runtime, {"id": pk})

        params: dict[str, Any] = {}
        if getattr(self, "_request_full_perms", False):
            params["full_perms"] = "true"

        api_path = self._resource_cls.format_api_path(pk=pk)
        data = await self._runtime.transport.get(api_path, params=params or None)

        return self._resource_cls.from_data(self._runtime, data)
