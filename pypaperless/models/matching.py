"""Model for matching resources."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from .base import PaperlessModel, PaperlessPost


class MatchingAlgorithm(Enum):
    """Enum with matching algorithms."""

    NONE = 0
    ANY = 1
    ALL = 2
    LITERAL = 3
    REGEX = 4
    FUZZY = 5
    AUTO = 6
    UNKNOWN = -1

    @classmethod
    def _missing_(cls: type, value: object) -> "MatchingAlgorithm":  # noqa ARG003
        """Set default member on unknown value."""
        return MatchingAlgorithm.UNKNOWN


@dataclass(kw_only=True)
class PaperlessModelMatchingMixin:
    """Mixin that adds matching attributes to a model."""

    match: str | None = None
    matching_algorithm: MatchingAlgorithm | None = None
    is_insensitive: bool | None = None

    def __post_init__(self) -> None:
        """Set default values when missing. Only on `POST`."""
        if not isinstance(self, PaperlessPost):
            return

        if not self.match:
            self.match = ""
        if not self.matching_algorithm:
            self.matching_algorithm = MatchingAlgorithm.NONE
        if not self.is_insensitive:
            self.is_insensitive = True


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
class DocumentType(PaperlessModel, PaperlessModelMatchingMixin):
    """Represent a document type resource on the Paperless api."""

    id: int | None = None
    slug: str | None = None
    name: str | None = None
    document_count: int | None = None
    owner: int | None = None
    user_can_change: bool | None = None


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
class CorrespondentPost(PaperlessPost, PaperlessModelMatchingMixin):
    """Attributes to send when creating a correspondent on the Paperless api."""

    name: str
    owner: int | None = None


@dataclass(kw_only=True)
class DocumentTypePost(PaperlessPost, PaperlessModelMatchingMixin):
    """Attributes to send when creating a document type on the api."""

    name: str
    owner: int | None = None


@dataclass(kw_only=True)
class StoragePathPost(PaperlessPost, PaperlessModelMatchingMixin):
    """Attributes to send when creating a storage path on the Paperless api."""

    name: str
    path: str
    owner: int | None = None


@dataclass(kw_only=True)
class TagPost(PaperlessPost, PaperlessModelMatchingMixin):
    """Attributes to send when creating a tag on the Paperless api."""

    name: str
    color: str = "#ffffff"
    text_color: str = "#000000"
    is_inbox_tag: bool = False
    owner: int | None = None
