"""Provide `DocumentType` related models."""

from typing import ClassVar

from pypaperless.const import EndpointPath, PaperlessResource

from . import mixins
from .base import PaperlessModel


class DocumentType(
    PaperlessModel,
    mixins.MatchingFieldsModel,
    mixins.SecurableModel,
):
    """Represent a Paperless `DocumentType`."""

    _api_path: ClassVar[str] = EndpointPath.DOCUMENT_TYPES_SINGLE
    _resource: ClassVar[PaperlessResource] = PaperlessResource.DOCUMENT_TYPES

    id: int | None = None
    slug: str | None = None
    name: str | None = None
    document_count: int | None = None


class DocumentTypeDraft(
    PaperlessModel,
    mixins.MatchingFieldsModel,
    mixins.SecurableDraftModel,
    mixins.CreatableModel,
):
    """Represent a new `DocumentType`, which is not yet stored in Paperless."""

    _api_path: ClassVar[str] = EndpointPath.DOCUMENT_TYPES
    _resource: ClassVar[PaperlessResource] = PaperlessResource.DOCUMENT_TYPES

    _create_required_fields: ClassVar[set[str]] = {
        "name",
        "match",
        "matching_algorithm",
        "is_insensitive",
    }

    name: str | None = None
    owner: int | None = None
