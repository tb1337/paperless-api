"""DeletableMixin for PyPaperless services."""

from pypaperless.models.base import ResourceT, ServiceProtocol


class DeletableMixin(ServiceProtocol[ResourceT]):
    """Provide the `delete` method for PyPaperless services."""

    async def delete(self, model: ResourceT) -> bool:
        """Delete a `resource item` from DRF. There is no point of return.

        Return `True` when deletion was successful, `False` otherwise.

        Example:
        -------
        ```python
        document = await paperless.documents(42)

        if await paperless.documents.delete(document):
            print("Successfully deleted the document!")
        ```

        """
        res = await self._client.request("delete", model._api_path)  # noqa: SLF001
        return res.status_code == 204
