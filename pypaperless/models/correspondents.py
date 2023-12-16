"""Model for correspondent resource."""

from dataclasses import dataclass
from datetime import datetime

from .base import PaperlessModel, PaperlessModelMatchingMixin, PaperlessPost


@dataclass(kw_only=True)
class Correspondent(PaperlessModel, PaperlessModelMatchingMixin):
    """Represent a correspondent resource on the Paperless api."""

    id: int | None = None
    slug: str | None = None
    name: str | None = None
    document_count: int | None = None
    last_correspondence: datetime | None = None
    owner: int | None = None
    user_can_change: bool | None = None


@dataclass(kw_only=True)
class CorrespondentPost(PaperlessPost, PaperlessModelMatchingMixin):
    """Attributes to send when creating a correspondent on the Paperless api."""

    name: str
    owner: int | None = None
