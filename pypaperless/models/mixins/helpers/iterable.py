"""IterableMixin for PyPaperless helpers."""

from collections.abc import AsyncGenerator, AsyncIterator
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Any, Self

from pypaperless.models.base import HelperProtocol, ResourceT
from pypaperless.models.generators import PageGenerator

if TYPE_CHECKING:
    from pypaperless.models import Page


class IterableMixin(HelperProtocol[ResourceT]):
    """Provide methods for iterating over resource items."""

    _aiter_filters: dict[str, str | int] | None

    async def __aiter__(self) -> AsyncIterator[ResourceT]:
        """Iterate over resource items.

        Example:
        -------
        ```python
        async for item in paperless.documents:
            # do something
        ```

        """
        async for page in self.pages():
            for item in page:
                yield item

    @asynccontextmanager
    async def reduce(
        self: Self,
        **kwargs: str | int,
    ) -> AsyncGenerator[Self]:
        """Provide context for iterating over resource items with query parameters.

        `kwargs`: Insert any Paperless api supported filter keywords here.
        You can provide `page` and `page_size` parameters, as well.

        Example:
        -------
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

    async def all(self) -> list[int]:
        """Return a list of all resource item primary keys.

        When used within a `reduce` context, returns a list of filtered primary keys.
        """
        page = await anext(self.pages(page=1))
        return page.all

    async def as_dict(self) -> dict[int, ResourceT]:
        """Shortcut for returning a primary key/object dict of all resource items.

        When used within a `reduce` context, data is filtered.
        """
        return {item.id: item async for item in self}  # type: ignore[attr-defined]

    async def as_list(self) -> list[ResourceT]:
        """Shortcut for returning a list of all resource items.

        When used within a `reduce` context, data is filtered.
        """
        return [item async for item in self]

    def pages(
        self,
        page: int = 1,
        page_size: int = 150,
    ) -> "AsyncIterator[Page[ResourceT]]":
        """Iterate over resource pages.

        `page`: A page number to start with.
        `page_size`: The page size for each requested batch.

        Example:
        -------
        ```python
        async for item in paperless.documents.pages():
            # do something
        ```

        """
        params: dict[str, Any] = getattr(self, "_aiter_filters", None) or {}

        for param, value in params.items():
            if param.endswith("__in"):
                try:
                    value.extend([])  # throw AttributeError if not a list
                    params[param] = ",".join(map(str, value))
                except AttributeError:
                    # value is not a list, don't modify
                    continue

        params.setdefault("page", page)
        params.setdefault("page_size", page_size)

        # set requesting full permissions
        if getattr(self, "_request_full_perms", False):
            params.update({"full_perms": "true"})

        return PageGenerator(self._api, self._api_path, self._resource_cls, params=params)
