"""Provide the `Page` generic class."""

from dataclasses import dataclass, field
from typing import Any

from pypaperless.const import API_PATH

from .base import PaperlessModel


@dataclass(init=False)
class Page(PaperlessModel):
    """Page."""

    _api_path = API_PATH["index"]

    count: int
    next: str | None = None
    previous: str | None = None
    all: list[int] = field(default_factory=list)
    results: list[dict[str, Any]] = field(default_factory=list)
