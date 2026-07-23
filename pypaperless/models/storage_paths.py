"""Provide `StoragePath` related models."""

from typing import ClassVar

from pypaperless.const import EndpointPath, PaperlessResource

from . import mixins
from .base import IdentifiedModel, PaperlessModel


class StoragePath(
    IdentifiedModel,
    mixins.MatchingFieldsModel,
    mixins.SecurableModel,
):
    """Represent a Paperless `StoragePath`."""

    _api_path: ClassVar[str] = EndpointPath.STORAGE_PATHS_SINGLE
    _resource: ClassVar[PaperlessResource] = PaperlessResource.STORAGE_PATHS

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
