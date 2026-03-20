"""IterableService for PyPaperless services."""

from collections.abc import AsyncGenerator, AsyncIterator
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Any, Self, TypedDict, Unpack

from pypaperless.models.base import ResourceT
from pypaperless.services.base import ResourceServiceProtocol
from pypaperless.services.generators import PageGenerator

if TYPE_CHECKING:
    from pypaperless.models import Page


class _BaseFilters(TypedDict, total=False):
    """Empty base TypedDict used by IterableService.filter().

    Being empty, every concrete filter TypedDict is a structural supertype
    of this class (PEP 692), so subclass overrides that narrow **kwargs to
    a specific filter TypedDict satisfy the Liskov substitution principle
    without requiring ``# type: ignore[override]``.
    """


class IterableService(ResourceServiceProtocol[ResourceT]):
    """Provide methods for iterating over resource items."""

    _aiter_filters: dict[str, Any] | None

    async def __aiter__(self) -> AsyncIterator[ResourceT]:
        """Iterate over all resource items, page by page.

        Example::

            async for item in paperless.documents:
                print(item.title)

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
        """Context manager for iterating over resource items with query parameters.

        The context variable is the service itself, scoped to the given filters.
        Use :meth:`__aiter__` or :meth:`pages` inside the block.

        Example::

            async with paperless.documents.filter(
                page_size=25,
                title__icontains="2023",
            ) as filtered:
                async for item in filtered:
                    print(item.title)

                async for page in filtered.pages():
                    print(page.count)

        """
        async with self._store_filters(**kwargs) as ctx:
            yield ctx

    async def all(self) -> list[int]:
        """Return a list of all resource item primary keys.

        When used within a :meth:`filter` context, returns only the filtered
        primary keys.

        Example::

            pks = await paperless.documents.all()
            # [1, 2, 3, …]

        """
        page = await anext(self.pages(page=1))
        return page.all

    async def as_dict(self) -> dict[int, ResourceT]:
        """Return a ``{pk: model}`` mapping of all resource items.

        When used within a :meth:`filter` context, only filtered items are included.

        Example::

            docs = await paperless.documents.as_dict()
            doc = docs[42]

        """
        return {item.id: item async for item in self}  # type: ignore[attr-defined]

    async def as_list(self) -> list[ResourceT]:
        """Return a flat list of all resource items.

        When used within a :meth:`filter` context, only filtered items are included.

        Example::

            tags = await paperless.tags.as_list()

        """
        return [item async for item in self]

    def pages(
        self,
        page: int = 1,
        page_size: int = 150,
    ) -> "AsyncIterator[Page[ResourceT]]":
        """Iterate over resource pages.

        Each yielded :class:`~pypaperless.models.pages.Page` contains up to
        *page_size* items.  Use within a :meth:`filter` context to apply
        server-side filters.

        Args:
            page:      Page number to start from (1-based).
            page_size: Maximum number of items per page.

        Example::

            async for page in paperless.documents.pages(page_size=50):
                print(f"Page {page.current_page} / {page.last_page}")
                for doc in page:
                    print(doc.title)

        """
        params: dict[str, Any] = dict(getattr(self, "_aiter_filters", None) or {})

        for param, value in params.items():
            if param.endswith("__in") and isinstance(value, list):
                params[param] = ",".join(map(str, value))

        params.setdefault("page", page)
        params.setdefault("page_size", page_size)

        # set requesting full permissions
        if getattr(self, "_request_full_perms", False):
            params.update({"full_perms": "true"})

        return PageGenerator(self._client, self._api_path, self._resource_cls, params=params)
