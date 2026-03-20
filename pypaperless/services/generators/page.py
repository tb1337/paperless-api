"""Provide the PageGenerator class."""

from collections.abc import AsyncIterator
from copy import deepcopy
from typing import TYPE_CHECKING, Any, Self

from pypaperless.models.pages import Page
from pypaperless.services.base import PaperlessService

if TYPE_CHECKING:
    from pypaperless import Paperless


class PageGenerator(PaperlessService, AsyncIterator):
    """Async iterator that yields :class:`~pypaperless.models.pages.Page` objects.

    Used internally by :meth:`~pypaperless.services.mixins.iterable.IterableMixin.pages`
    to fetch and paginate through API results.

    Args:
        client:       A :class:`~pypaperless.client.Paperless` instance.
        url:          The API endpoint URL returning paginated results.
        resource_cls: The model class used to map raw result dicts.
        params:       Optional query string parameters.

    """

    _page: Page | None

    def __aiter__(self) -> Self:
        """Return self as iterator."""
        return self

    async def __anext__(self) -> Page:
        """Return next item from the current batch."""
        if self._page is not None and self._page.is_last_page:
            raise StopAsyncIteration

        res = await self._client.request_json("get", self._url, params=self.params)
        data = {
            **res,
            "current_page": self.params["page"],
            "page_size": self.params["page_size"],
        }
        self._page = Page.from_data(self._client, data, resource_cls=self._resource_cls)

        # rise page by one to request next page on next iteration
        self.params["page"] += 1

        # we do not reach this point without a self._page object, so: ignore type error
        return self._page

    def __init__(
        self,
        client: "Paperless",
        url: str,
        resource_cls: type,
        params: dict[str, Any] | None = None,
    ) -> None:
        """Initialize `PageGenerator` class instance."""
        super().__init__(client)

        self._page = None
        self._resource_cls = resource_cls
        self._url = url

        self.params = deepcopy(params) if params else {}
        self.params.setdefault("page", 1)
        self.params.setdefault("page_size", 150)
