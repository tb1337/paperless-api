"""Provide `StoragePath` related models."""

from typing import TYPE_CHECKING, Any, ClassVar

from pypaperless.const import API_PATH

from . import mixins
from .base import PaperlessModel

if TYPE_CHECKING:
    from pypaperless import Paperless


class StoragePath(
    PaperlessModel,
    mixins.MatchingFieldsMixin,
    mixins.SecurableMixin,
):
    """Represent a Paperless `StoragePath`."""

    _api_path: ClassVar[str] = API_PATH["storage_paths_single"]

    id: int | None = None
    slug: str | None = None
    name: str | None = None
    path: str | None = None
    document_count: int | None = None

    def __init__(self, client: "Paperless", data: dict[str, Any], **kwargs: Any) -> None:
        """Initialize a `StoragePath` instance."""
        super().__init__(client, data, **kwargs)
        self._format_api_path(data)


class StoragePathDraft(
    PaperlessModel,
    mixins.MatchingFieldsMixin,
    mixins.SecurableDraftMixin,
    mixins.CreatableMixin,
):
    """Represent a new `StoragePath`, which is not yet stored in Paperless."""

    _api_path: ClassVar[str] = API_PATH["storage_paths"]

    _create_required_fields: ClassVar[set[str]] = {
        "name",
        "path",
        "match",
        "matching_algorithm",
        "is_insensitive",
    }

    name: str | None = None
    path: str | None = None
    owner: int | None = None
