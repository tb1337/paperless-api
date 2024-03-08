"""Provide the PageGenerator class."""

from collections.abc import AsyncIterator
from copy import deepcopy
from typing import TYPE_CHECKING, Any, Self

from pypaperless.models.base import PaperlessBase
from pypaperless.models.pages import Page

if TYPE_CHECKING:
    from pypaperless import Paperless


class PageGenerator(PaperlessBase, AsyncIterator):
    """Iterator for DRF paginated endpoints.

    `api`: An instance of :class:`Paperless`.
    `url`: A url returning DRF page contents.
    `resource`: A target resource model type for mapping results with.
    `params`: Optional dict of query string parameters.
    """

    _page: Page | None

    def __aiter__(self) -> Self:
        """Return self as iterator."""
        return self

    async def __anext__(self) -> Page:
        """Return next item from the current batch."""
        if self._page is not None and self._page.is_last_page:
            raise StopAsyncIteration

        res = await self._api.request_json("get", self._url, params=self.params)
        data = {
            **res,
            "_api_path": self._url,
            "current_page": self.params["page"],
            "page_size": self.params["page_size"],
        }
        self._page = Page.create_with_data(self._api, data, fetched=True)
        # dirty attach the resource to the data class
        self._page._resource_cls = self._resource_cls  # noqa: SLF001

        # rise page by one to request next page on next iteration
        self.params["page"] += 1

        # we do not reach this point without a self._page object, so: ignore type error
        return self._page

    def __init__(
        self,
        api: "Paperless",
        url: str,
        resource_cls: type,
        params: dict[str, Any] | None = None,
    ) -> None:
        """Initialize `PageGenerator` class instance."""
        super().__init__(api)

        self._page = None
        self._resource_cls = resource_cls
        self._url = url

        self.params = deepcopy(params) if params else {}
        self.params.setdefault("page", 1)
        self.params.setdefault("page_size", 150)
