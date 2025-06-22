"""Provide the `Paginated` class."""

import math
from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Any, Generic

from pypaperless.const import API_PATH

from .base import PaperlessModel, ResourceT


@dataclass(init=False)
class Page(PaperlessModel, Generic[ResourceT]):  # noqa: UP046
    """Represent a Paperless DRF `Paginated`."""

    _api_path = API_PATH["index"]
    _resource_cls: type[ResourceT]

    # our fields
    current_page: int
    page_size: int

    # DRF fields
    count: int
    next: str | None = None
    previous: str | None = None
    all: list[int] = field(default_factory=list)
    results: list[dict[str, Any]] = field(default_factory=list)

    def __iter__(self) -> Iterator[ResourceT]:
        """Return iter of `.items`."""
        return iter(self.items)

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
        """Return the results list field with mapped PyPaperless `models`.

        Example:
        -------
        ```python
        async for page in paperless.documents.pages():
            assert isinstance(page.results.pop(), Document) # fails, it is a dict
            assert isinstance(page.items.pop(), Document) # ok
        ```

        """

        def mapper(data: dict[str, Any]) -> ResourceT:
            return self._resource_cls.create_with_data(self._api, data, fetched=True)

        return list(map(mapper, self._data["results"]))

    @property
    def is_last_page(self) -> bool:
        """Return whether we are on the last page or not."""
        return not self.has_next_page

    @property
    def last_page(self) -> int:
        """Return the last page number."""
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
