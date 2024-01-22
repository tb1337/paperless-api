"""Provide the ResourceIterator class."""

from collections.abc import AsyncIterator
from copy import deepcopy
from typing import TYPE_CHECKING, Any

from pypaperless.models import ResultPage
from pypaperless.models.base import PaperlessBase

if TYPE_CHECKING:
    from pypaperless import Paperless


class ResourceGenerator(PaperlessBase, AsyncIterator):
    """Iterator for DRF paginated endpoints.

    `api`: An instance of :class:`Paperless`.
    `url`: A url returning DRF page contents.
    `limit`: The limit of items to return. If `None`, return all.
    `params`: Optional dict of query string parameters.
    """

    def __aiter__(self) -> AsyncIterator:
        """Return self as iterator."""
        return self

    async def __anext__(self) -> dict[str, Any]:
        """Return next item from the current batch."""
        if self.limit is not None and self.yielded >= self.limit:
            raise StopAsyncIteration

        if self._page is None or self._ix >= len(self._page.results):
            await self._request_batch()

        self._ix += 1
        self.yielded += 1

        # we do not reach this point without a self._page object, so: ignore type error
        return self._page.results[self._ix - 1]  # type: ignore[union-attr]

    def __init__(
        self,
        api: "Paperless",
        url: str,
        limit: int | None = None,
        params: dict[str, int | str] | None = None,
    ):
        """Initialize `ResourceIterator` class instance."""
        super().__init__(api)

        self._ix: int = 0
        self._page: ResultPage | None = None
        self._url = url
        self.limit = limit
        self.params = deepcopy(params) if params else {}
        self.yielded = 0

        self.params.setdefault("page", 1)
        self.params.setdefault("page_size", 150)

    async def _request_batch(self) -> None:
        """Request a single page from DRF and store it result in `self._list`."""
        url: str | None = self._url
        if self._page is not None:
            url = self._page.next

        if url is None:
            raise StopAsyncIteration

        res = await self._api.request_json("get", url, params=self.params)
        page = ResultPage.create_with_data(self._api, res, fetched=True)

        self._page = page
        self._ix = 0

        # reset params as `request_json` returns a full path with query string
        self.params = {}
