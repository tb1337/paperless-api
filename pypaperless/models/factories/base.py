"""Provide the FactoryBase class."""

from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, Generic, final

# from pypaperless.const import ResourceT
from pypaperless.models.base import PaperlessBase, ResourceT
from pypaperless.utils.generators import ResourceGenerator

if TYPE_CHECKING:
    from pypaperless import Paperless


class FactoryBase(PaperlessBase, Generic[ResourceT]):
    """Base class for all factories in PyPaperless."""

    _api_path = ""
    _resource: ResourceT

    @final
    async def __aiter__(self) -> AsyncIterator[ResourceT]:
        """Iterate over resource items."""
        items = ResourceGenerator(self._api, self.api_path)
        async for data in items:
            yield self._resource.create_with_data(self._api, data, fetched=True)

    @final
    async def __call__(self, pk: int, lazy: bool = False) -> ResourceT:
        """Request exactly one resource item."""
        item = self._resource.create_with_data(self._api, {"id": pk})
        if not lazy:
            await item.load()
        return item

    def __init__(self, api: "Paperless"):
        """Initialize a `FactoryBase` instance."""
        super().__init__(api)

        # TODO: implement basic fetch
