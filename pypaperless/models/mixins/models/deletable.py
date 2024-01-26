"""DeletableMixin for PyPaperless models."""

from typing import final

from pypaperless.models.base import PaperlessModelProtocol


class DeletableMixin(PaperlessModelProtocol):  # pylint: disable=too-few-public-methods
    """Provide the `delete` method for PyPaperless models."""

    @final
    async def delete(self) -> bool:
        """Delete a `resource item` from DRF. There is no point of return.

        Return `True` when deletion was successful, `False` otherwise.

        Example:
        ```python
        # request a document
        document = await paperless.documents(42)

        if await document.delete():
            print("Successfully deleted the document!")
        ```
        """
        async with self._api.request("delete", self._api_path) as res:
            success = res.status == 204

        return success