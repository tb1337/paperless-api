"""Generator."""

from collections.abc import AsyncIterator
from copy import deepcopy
from typing import TYPE_CHECKING, Generic

from pypaperless.const import ResourceT
from pypaperless.models.base import PaperlessBase

if TYPE_CHECKING:
    from pypaperless import Paperless


class ResourceIterator(PaperlessBase, AsyncIterator, Generic[ResourceT]):
    """Listing."""

    def __aiter__(self) -> AsyncIterator[ResourceT]:
        """Return self as iterator."""
        return self

    async def __anext__(self) -> ResourceT:
        """Next."""
        if self.limit is not None and self.yielded >= self.limit:
            raise StopAsyncIteration

        if self._ix >= len(self._list):
            await self._request_batch()

        self._ix += 1
        self.yielded += 1
        return self._cls.parse(self._list[self._ix - 1], self._api)

    def __init__(  # pylint: disable=too-many-arguments
        self,
        cls: type[ResourceT],
        api: "Paperless",
        url: str,
        limit: int | None = None,
        params: dict[str, int | str] | None = None,
    ):
        """Init."""
        super().__init__(api, None)

        self._cls = cls
        self._ix: int = 0
        self._list: list = []
        self._url = url
        self.limit = limit
        self.params = deepcopy(params) if params else {}
        self.yielded = 0

        self.params.setdefault("page", 1)
        self.params.setdefault("page_size", 150)

    async def _request_batch(self) -> None:
        """Get next batch."""
        if self.exhausted:
            raise StopAsyncIteration

        print(f"Requesting batch, current yielded: {self.yielded}")

        res = await self._api.request_json("get", self._url, params=self.params)
        self._url = res["next"]
        self._list = res["results"]
        self._ix = 0

        # reset params as `request_json` returns a full path with query string
        self.params = {}

    @property
    def exhausted(self) -> bool:
        """Is Exhausted."""
        return self._url is None
