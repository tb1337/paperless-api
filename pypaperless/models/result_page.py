"""Provide the `ResultPage` class."""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from pypaperless.const import API_PATH

from .base import PaperlessModel

if TYPE_CHECKING:
    pass


@dataclass(init=False)
class ResultPage(PaperlessModel):  # pylint: disable=too-many-instance-attributes
    """Represent a Paperless DRF `ResultPage`."""

    _api_path = API_PATH["index"]

    # DRF fields
    count: int
    next: str | None = None
    previous: str | None = None
    all: list[int] = field(default_factory=list)
    results: list[dict[str, Any]] = field(default_factory=list)

    # our fields
    current_page: int | None = None
    next_page: int | None = None
    last_page: int | None = None
    page_size: int = 25  # DRF default page size
