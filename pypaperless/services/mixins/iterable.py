"""IterableMixin for PyPaperless services."""

from collections.abc import AsyncGenerator, AsyncIterator
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Any, Self, TypedDict, Unpack

from pypaperless.models.base import ResourceT
from pypaperless.services.base import ResourceServiceProtocol
from pypaperless.services.generators import PageGenerator

if TYPE_CHECKING:
    from pypaperless.models import Page


class _BaseFilters(TypedDict, total=False):
    """Empty base TypedDict used by IterableMixin.filter().

    Being empty, every concrete filter TypedDict is a structural supertype
    of this class (PEP 692), so subclass overrides that narrow **kwargs to
    a specific filter TypedDict satisfy the Liskov substitution principle
    without requiring ``# type: ignore[override]``.
    """


class IterableMixin(ResourceServiceProtocol[ResourceT]):
    """Provide methods for iterating over resource items."""

    _aiter_filters: dict[str, Any] | None

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
    async def _store_filters(self: Self, **kwargs: Any) -> AsyncGenerator[Self]:
        """Store query filters for the duration of the context.

        This is the private implementation backing :meth:`reduce`.  Subclasses
        call ``self._store_filters(**kwargs)`` rather than ``super().filter()``
        so that the typed public override does not need to widen its signature
        back to ``**kwargs: Any``.
        """
        self._aiter_filters = kwargs
        try:
            yield self
        finally:
            self._aiter_filters = None

    @asynccontextmanager
    async def filter(
        self: Self,
        **kwargs: Unpack[_BaseFilters],
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

        async with paperless.documents.filter(**filters):
            # iterate over resource items ...
            async for item in paperless.documents:
                ...

            # ... or iterate pages as-is
            async for page in paperless.documents.pages():
                ...
        ```

        """
        async with self._store_filters(**kwargs) as ctx:
            yield ctx

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
        params: dict[str, Any] = dict(getattr(self, "_aiter_filters", None) or {})

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

        return PageGenerator(self._client, self._api_path, self._resource_cls, params=params)
