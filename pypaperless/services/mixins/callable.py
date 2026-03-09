"""CallableMixin for PyPaperless services."""

from typing import Any

from pypaperless.models.base import ResourceT
from pypaperless.services.base import ServiceProtocol


class CallableMixin(ServiceProtocol[ResourceT]):
    """Provide methods for calling a specific resource item."""

    async def __call__(
        self,
        pk: int,
        *,
        lazy: bool = False,
    ) -> ResourceT:
        """Request exactly one resource item.

        Example:
        -------
        ```python
        # request a document
        document = await paperless.documents(42)

        # initialize a model without fetching data
        document = await paperless.documents(42, lazy=True)
        ```

        """
        if lazy:
            return self._resource_cls.create_with_data(self._client, {"id": pk})

        params: dict[str, Any] = {}
        if getattr(self, "_request_full_perms", False):
            params["full_perms"] = "true"

        api_path = self._resource_cls.format_api_path(pk=pk)
        data = await self._client.request_json("get", api_path, params=params or None)

        return self._resource_cls.create_with_data(self._client, data)
