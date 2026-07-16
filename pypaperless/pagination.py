"""Provide pagination primitives: Page and PageGenerator."""

import math
from collections.abc import AsyncIterator, Iterator
from copy import deepcopy
from typing import TYPE_CHECKING, Any

from pydantic import Field, PrivateAttr

from pypaperless.models.base import _PaperlessBase

if TYPE_CHECKING:
    from pypaperless.models.base import PaperlessModel
    from pypaperless.runtime import PaperlessRuntime


class Page[ResourceT: "PaperlessModel"](_PaperlessBase):
    """Represent a single paginated response page from the Paperless API."""

    _resource_cls: type[ResourceT] | None = PrivateAttr(default=None)
    _current_page: int = PrivateAttr(default=0)
    _page_size: int = PrivateAttr(default=0)

    count: int = 0
    next: str | None = None
    previous: str | None = None
    results: list[dict[str, Any]] = Field(default_factory=list)

    def model_post_init(self, __context: Any, /) -> None:
        """Bind ``_runtime``, ``_resource_cls``, and pagination state from context."""
        super().model_post_init(__context)
        if isinstance(__context, dict):
            if "resource_cls" in __context:
                self._resource_cls = __context["resource_cls"]
            if "current_page" in __context:
                self._current_page = __context["current_page"]
            if "page_size" in __context:
                self._page_size = __context["page_size"]

    @property
    def current_page(self) -> int:
        """Return the current page number."""
        return self._current_page

    @property
    def page_size(self) -> int:
        """Return the page size used for this request."""
        return self._page_size

    @property
    def current_count(self) -> int:
        """Return the item count of the current page."""
        return len(self.results)

    @property
    def has_next_page(self) -> bool:
        """Return whether there is a next page or not."""
        return self.next_page is not None

    @property
    def has_previous_page(self) -> bool:
        """Return whether there is a previous page or not."""
        return self.previous_page is not None

    @property
    def items(self) -> list[ResourceT]:
        """Return this page's results deserialized as model instances.

        Unlike the raw :attr:`results` list (which contains plain dicts), this
        property deserializes each entry into the appropriate model class.

        Example::

            async for page in paperless.documents.pages():
                for doc in page.items:
                    print(doc.title)  # doc is a Document instance

        """

        def mapper(data: dict[str, Any]) -> ResourceT:
            if self._resource_cls is None:
                msg = "Page was created without a resource_cls; pass resource_cls= to from_data()"
                raise RuntimeError(msg)
            return self._resource_cls.from_data(self._runtime, data)

        return list(map(mapper, self.results))

    @property
    def is_last_page(self) -> bool:
        """Return whether we are on the last page or not."""
        return not self.has_next_page

    @property
    def last_page(self) -> int:
        """Return the last page number."""
        if self.page_size <= 0:
            msg = "Page was created without pagination context; pass page_size= to from_data()"
            raise RuntimeError(msg)
        return math.ceil(self.count / self.page_size)

    @property
    def next_page(self) -> int | None:
        """Return the next page number if a next page exists."""
        if self.next is None:
            return None
        return self.current_page + 1

    @property
    def previous_page(self) -> int | None:
        """Return the previous page number if a previous page exists."""
        if self.previous is None:
            return None
        return self.current_page - 1

    def __iter__(self) -> Iterator[ResourceT]:  # type: ignore[override]
        """Return iter of `.items`."""
        return iter(self.items)


class PageGenerator(AsyncIterator["Page"]):
    """Async iterator that yields :class:`Page` objects.

    Used internally by :meth:`~pypaperless.services.mixins.iterable.IterableService.pages`
    to fetch and paginate through API results.

    Args:
        runtime:      A :class:`~pypaperless.runtime.PaperlessRuntime` instance.
        url:          The API endpoint URL returning paginated results.
        resource_cls: The model class used to map raw result dicts.
        params:       Optional query string parameters.

    """

    def __init__(
        self,
        runtime: "PaperlessRuntime",
        url: str,
        resource_cls: type,
        params: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a :class:`PageGenerator` instance."""
        self._runtime = runtime
        self._page: Page | None = None
        self._resource_cls = resource_cls
        self._url = url

        self.params = deepcopy(params) if params else {}
        self.params.setdefault("page", 1)
        self.params.setdefault("page_size", 150)

    def __aiter__(self) -> "PageGenerator":
        """Return self as iterator."""
        return self

    async def __anext__(self) -> "Page":
        """Return next item from the current batch."""
        if self._page is not None and self._page.is_last_page:
            raise StopAsyncIteration

        res = await self._runtime.transport.get(self._url, params=self.params)
        self._page = Page.from_data(
            self._runtime,
            res,
            resource_cls=self._resource_cls,
            current_page=self.params["page"],
            page_size=self.params["page_size"],
        )

        self.params["page"] += 1

        return self._page
