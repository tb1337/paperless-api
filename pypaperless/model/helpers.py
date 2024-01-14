"""Helpers."""

from collections.abc import Generator, Iterator
from copy import deepcopy
from typing import TYPE_CHECKING, Any, Generic, TypeVar

from .base import PaperlessBase
from .documents import Document

if TYPE_CHECKING:
    from pypaperless import Paperless

ResourceT = TypeVar("ResourceT", bound=PaperlessBase)


class ListingGenerator(Generic[ResourceT], PaperlessBase, Iterator):
    """Listing."""

    def __init__(self, api: "Paperless", params: dict[str, Any]):
        """Init."""
        super().__init__(api, None)
        self._listing = [1, 2]
        self.params = deepcopy(params) if params else {}
        self.yielded = 0

    def __iter__(self) -> Iterator[ResourceT]:
        """Iter."""
        return self

    def __next__(self) -> ResourceT:
        """Next."""
        self.yielded += 1
        if self.yielded > len(self._listing):
            raise StopIteration()
        return self._listing[self.yielded - 1]


class DocumentHelper(ListingGenerator[Document], PaperlessBase):
    """Helper."""

    def __call__(self, pk: int) -> Document:
        """Call."""
        return Document(self._api, {"id": pk})
