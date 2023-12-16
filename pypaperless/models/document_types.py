"""Model for document type resource."""

from dataclasses import dataclass

from .base import PaperlessModel, PaperlessModelMatchingMixin, PaperlessPost


@dataclass(kw_only=True)
class DocumentType(PaperlessModel, PaperlessModelMatchingMixin):
    """Represent a document type resource on the Paperless api."""

    id: int | None = None
    slug: str | None = None
    name: str | None = None
    document_count: int | None = None
    owner: int | None = None
    user_can_change: bool | None = None


@dataclass(kw_only=True)
class DocumentTypePost(PaperlessPost, PaperlessModelMatchingMixin):
    """Attributes to send when creating a document type on the api."""

    name: str
    owner: int | None = None
