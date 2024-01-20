"""Iterable mixin for PyPaperless helpers."""

from collections.abc import AsyncGenerator, AsyncIterator
from contextlib import asynccontextmanager
from typing import Self, final

from pypaperless.models.base import ResourceT
from pypaperless.models.generators import ResourceGenerator
from pypaperless.models.helpers.base import HelperProtocol


class IterableMixin(HelperProtocol[ResourceT]):
    """Provide methods for iterating over resource items."""

    _aiter_filters: dict[str, str | int] | None

    @final
    async def __aiter__(self) -> AsyncIterator[ResourceT]:
        """Iterate over resource items.

        Example:
        ```python
        async for item in paperless.documents:
            # do something
        ```
        """
        items = ResourceGenerator(
            self._api,
            self._api_path,
            params=getattr(self, "_aiter_filters", None),
        )
        async for data in items:
            yield self._resource.create_with_data(self._api, data, fetched=True)

    @final
    @asynccontextmanager
    async def filter_iteration(
        self: Self,
        **kwargs: str | int,
    ) -> AsyncGenerator[Self, None]:
        """Provide context for iterating over resource items with query parameters.

        Example:
        ```python
        async with paperless.documents.filter_iteration(**filters):
            async for item in paperless.documents:
                # do something
        ```
        """
        self._aiter_filters = kwargs
        yield self
        self._aiter_filters = None
