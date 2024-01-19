"""CallableMixin for PyPaperless helpers."""

from typing import final

from pypaperless.models.base import ResourceT
from pypaperless.models.helpers.base import HelperProtocol


class CallableMixin(HelperProtocol[ResourceT]):
    """Provide methods for calling a specific resource item."""

    @final
    async def __call__(
        self,
        pk: int,
        lazy: bool = False,
    ) -> ResourceT:
        """Request exactly one resource item.

        Example:
        ```python
        # request a document
        document = await paperless.documents(42)

        # initialize a model and request it later
        document = await paperless.documents(42, lazy=True)
        ```
        """
        data = {
            "id": pk,
        }
        item = self._resource.create_with_data(self._api, data)
        if not lazy:
            await item.load()
        return item
