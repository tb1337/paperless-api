"""DeletableMixin for PyPaperless models."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pypaperless.models.base import PaperlessModelProtocol as _Base
else:
    _Base = object


class DeletableMixin(_Base):
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
        res = await self._client.request("delete", self._api_path)
        return res.status_code == 204
