"""Model for tag resource."""

from dataclasses import dataclass

from .base import PaperlessModel, PaperlessModelMatchingMixin, PaperlessPost


@dataclass(kw_only=True)
class Tag(
    PaperlessModel, PaperlessModelMatchingMixin
):  # pylint: disable=too-many-instance-attributes
    """Represent a tag resource on the Paperless api."""

    id: int | None = None
    slug: str | None = None
    name: str | None = None
    color: str | None = None
    text_color: str | None = None
    is_inbox_tag: bool | None = None
    document_count: int | None = None
    owner: int | None = None
    user_can_change: bool | None = None


@dataclass(kw_only=True)
class TagPost(PaperlessPost, PaperlessModelMatchingMixin):
    """Attributes to send when creating a tag on the Paperless api."""

    name: str
    color: str = "#ffffff"
    text_color: str = "#000000"
    is_inbox_tag: bool = False
    owner: int | None = None
