"""IterableMixin for PyPaperless helpers."""

from collections.abc import AsyncGenerator, AsyncIterator
from contextlib import asynccontextmanager
from typing import Self, final

from pypaperless.models import ResultPage
from pypaperless.models.base import ResourceT
from pypaperless.models.generators import PageGenerator
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
        async for page in self.pages():
            for item in page:
                yield item

    @final
    @asynccontextmanager
    async def reduce(
        self: Self,
        **kwargs: str | int,
    ) -> AsyncGenerator[Self, None]:
        """Provide context for iterating over resource items with query parameters.

        `kwargs`: Insert any Paperless api supported filter keywords here.
        You can provide `page` and `page_size` parameters, as well.

        Example:
        ```python
        filters = {
            "page_size": 1337,
            "title__icontains": "2023",
        }

        async with paperless.documents.reduce(**filters):
            # iterate over resource items ...
            async for item in paperless.documents:
                ...

            # ... or iterate pages as-is
            async for page in paperless.documents.pages():
                ...
        ```
        """
        self._aiter_filters = kwargs
        yield self
        self._aiter_filters = None

    @final
    def pages(
        self,
        page: int = 1,
        page_size: int = 150,
    ) -> AsyncIterator[ResultPage[ResourceT]]:
        """Iterate over resource pages.

        `page`: A page number to start with.
        `page_size`: The page size for each requested batch.

        Example:
        ```python
        async for item in paperless.documents.pages():
            # do something
        ```
        """
        params = getattr(self, "_aiter_filters", {})
        params.setdefault("page", page)
        params.setdefault("page_size", page_size)

        return PageGenerator(self._api, self._api_path, self._resource, params=params)
