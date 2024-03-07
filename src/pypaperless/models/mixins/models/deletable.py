"""DeletableMixin for PyPaperless models."""

from pypaperless.models.base import PaperlessModelProtocol


class DeletableMixin(PaperlessModelProtocol):
    """Provide the `delete` method for PyPaperless models."""

    async def delete(self) -> bool:
        """Delete a `resource item` from DRF. There is no point of return.

        Return `True` when deletion was successful, `False` otherwise.

        Example:
        -------
        ```python
        # request a document
        document = await paperless.documents(42)

        if await document.delete():
            print("Successfully deleted the document!")
        ```

        """
        async with self._api.request("delete", self._api_path) as res:
            return res.status == 204
