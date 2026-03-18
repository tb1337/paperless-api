"""Provide the `Paginated` class."""

import math
from collections.abc import Iterator
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field, PrivateAttr

if TYPE_CHECKING:
    from pypaperless import Paperless

    from .base import PaperlessModel


class Page[ResourceT: "PaperlessModel"](BaseModel):
    """Represent a single paginated response page from the Paperless API."""

    _client: "Paperless" = PrivateAttr()
    _resource_cls: type[ResourceT] = PrivateAttr()

    # our fields
    current_page: int = 0
    page_size: int = 0

    # DRF fields
    count: int = 0
    next: str | None = None
    previous: str | None = None
    all: list[int] = Field(default_factory=list)
    results: list[dict[str, Any]] = Field(default_factory=list)

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
            return self._resource_cls.from_data(self._client, data)

        return list(map(mapper, self.results))

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

    def __iter__(self) -> Iterator[ResourceT]:  # type: ignore[override]
        """Return iter of `.items`."""
        return iter(self.items)

    @classmethod
    def from_data(cls, client: "Paperless", data: Any) -> "Page[ResourceT]":
        """Create a Page instance from raw API response data."""
        instance = cls.model_validate(data)
        object.__setattr__(instance, "_client", client)
        return instance

    def set_resource_cls(self, resource_cls: type[ResourceT]) -> None:
        """Set the resource class for items mapping."""
        self._resource_cls = resource_cls
