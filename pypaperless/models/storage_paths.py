"""Provide `StoragePath` related models."""

from typing import ClassVar

from pypaperless.const import API_PATH, PaperlessResource

from . import mixins
from .base import PaperlessModel


class StoragePath(
    PaperlessModel,
    mixins.MatchingFieldsModel,
    mixins.SecurableModel,
    mixins.UpdatableModel,
    mixins.DeletableModel,
):
    """Represent a Paperless `StoragePath`."""

    _api_path: ClassVar[str] = API_PATH["storage_paths_single"]
    _resource: ClassVar[PaperlessResource] = PaperlessResource.STORAGE_PATHS

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
    mixins.SaveableModel,
):
    """Represent a new `StoragePath`, which is not yet stored in Paperless."""

    _api_path: ClassVar[str] = API_PATH["storage_paths"]
    _resource: ClassVar[PaperlessResource] = PaperlessResource.STORAGE_PATHS

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
