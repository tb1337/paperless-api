"""Model for group resource."""

from dataclasses import dataclass

from .base import PaperlessModel


@dataclass(kw_only=True)
class Group(PaperlessModel):
    """Represent a group resource on the Paperless api."""

    id: int | None = None
    name: str | None = None
    permissions: list[str] | None = None
