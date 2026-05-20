"""Provide `StoragePath` related models."""

from typing import ClassVar

from pypaperless.const import EndpointPath

from . import mixins
from .base import PaperlessModel


class StoragePath(
    PaperlessModel,
    mixins.MatchingFieldsModel,
    mixins.SecurableModel,
):
    """Represent a Paperless `StoragePath`."""

    _api_path: ClassVar[str] = EndpointPath.STORAGE_PATHS_SINGLE

    id: int | None = None
    slug: str | None = None
    name: str | None = None
    path: str | None = None
    document_count: int | None = None


class StoragePathDraft(
    PaperlessModel,
    mixins.MatchingFieldsModel,
    mixins.SecurableDraftModel,
    mixins.CreatableModel,
):
    """Represent a new `StoragePath`, which is not yet stored in Paperless."""

    _api_path: ClassVar[str] = EndpointPath.STORAGE_PATHS

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
