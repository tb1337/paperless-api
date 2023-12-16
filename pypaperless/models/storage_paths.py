"""Model for storage path resource."""

from dataclasses import dataclass

from .base import PaperlessModel, PaperlessModelMatchingMixin, PaperlessPost


@dataclass(kw_only=True)
class StoragePath(PaperlessModel, PaperlessModelMatchingMixin):
    """Represent a storage path resource on the Paperless api."""

    id: int | None = None
    slug: str | None = None
    name: str | None = None
    path: str | None = None
    document_count: int | None = None
    owner: int | None = None
    user_can_change: bool | None = None


@dataclass(kw_only=True)
class StoragePathPost(PaperlessPost, PaperlessModelMatchingMixin):
    """Attributes to send when creating a storage path on the Paperless api."""

    name: str
    path: str
    owner: int | None = None
