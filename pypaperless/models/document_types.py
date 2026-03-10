"""Provide `DocumentType` related models."""

from typing import TYPE_CHECKING, Any, ClassVar

from pypaperless.const import API_PATH

from . import mixins
from .base import PaperlessModel

if TYPE_CHECKING:
    from pypaperless import Paperless


class DocumentType(
    PaperlessModel,
    mixins.MatchingFieldsMixin,
    mixins.SecurableMixin,
):
    """Represent a Paperless `DocumentType`."""

    _api_path: ClassVar[str] = API_PATH["document_types_single"]

    id: int | None = None
    slug: str | None = None
    name: str | None = None
    document_count: int | None = None

    def __init__(self, client: "Paperless", data: dict[str, Any], **kwargs: Any) -> None:
        """Initialize a `DocumentType` instance."""
        super().__init__(client, data, **kwargs)
        self._set_api_path(data)


class DocumentTypeDraft(
    PaperlessModel,
    mixins.MatchingFieldsMixin,
    mixins.SecurableDraftMixin,
    mixins.CreatableMixin,
):
    """Represent a new `DocumentType`, which is not yet stored in Paperless."""

    _api_path: ClassVar[str] = API_PATH["document_types"]

    _create_required_fields: ClassVar[set[str]] = {
        "name",
        "match",
        "matching_algorithm",
        "is_insensitive",
    }

    name: str | None = None
    owner: int | None = None
