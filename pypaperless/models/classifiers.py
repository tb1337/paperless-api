"""Provide `Correspondent`, `DocumentType`, `StoragePath` and `Tag` related models and services."""

import datetime
from typing import TYPE_CHECKING, Any, ClassVar

from pypaperless.const import API_PATH, PaperlessResource

from .base import ServiceBase, PaperlessModel
from .mixins import services, models

if TYPE_CHECKING:
    from pypaperless import Paperless


class Correspondent(
    PaperlessModel,
    models.MatchingFieldsMixin,
    models.SecurableMixin,
    models.UpdatableMixin,
    models.DeletableMixin,
):
    """Represent a Paperless `Correspondent`."""

    _api_path: ClassVar[str] = API_PATH["correspondents_single"]

    id: int | None = None
    slug: str | None = None
    name: str | None = None
    document_count: int | None = None
    last_correspondence: datetime.date | None = None

    def __init__(self, client: "Paperless", data: dict[str, Any], **kwargs: Any) -> None:
        """Initialize a `Correspondent` instance."""
        super().__init__(client, data, **kwargs)
        self._format_api_path(data)


class CorrespondentDraft(
    PaperlessModel,
    models.MatchingFieldsMixin,
    models.SecurableDraftMixin,
    models.CreatableMixin,
):
    """Represent a new `Correspondent`, which is not yet stored in Paperless."""

    _api_path: ClassVar[str] = API_PATH["correspondents"]

    _create_required_fields: ClassVar[set[str]] = {
        "name",
        "match",
        "matching_algorithm",
        "is_insensitive",
    }

    name: str | None = None


class DocumentType(
    PaperlessModel,
    models.MatchingFieldsMixin,
    models.SecurableMixin,
    models.UpdatableMixin,
    models.DeletableMixin,
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
        self._format_api_path(data)


class DocumentTypeDraft(
    PaperlessModel,
    models.MatchingFieldsMixin,
    models.SecurableDraftMixin,
    models.CreatableMixin,
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


class StoragePath(
    PaperlessModel,
    models.MatchingFieldsMixin,
    models.SecurableMixin,
    models.UpdatableMixin,
    models.DeletableMixin,
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
    models.MatchingFieldsMixin,
    models.SecurableDraftMixin,
    models.CreatableMixin,
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


class Tag(
    PaperlessModel,
    models.MatchingFieldsMixin,
    models.SecurableMixin,
    models.UpdatableMixin,
    models.DeletableMixin,
):
    """Represent a Paperless `Tag`."""

    _api_path: ClassVar[str] = API_PATH["tags_single"]

    id: int | None = None
    slug: str | None = None
    name: str | None = None
    color: str | None = None
    text_color: str | None = None
    is_inbox_tag: bool | None = None
    document_count: int | None = None
    parent: int | None = None
    children: list["Tag"] | None = None

    def __init__(self, client: "Paperless", data: dict[str, Any], **kwargs: Any) -> None:
        """Initialize a `Tag` instance."""
        super().__init__(client, data, **kwargs)
        self._format_api_path(data)


class TagDraft(
    PaperlessModel,
    models.MatchingFieldsMixin,
    models.SecurableDraftMixin,
    models.CreatableMixin,
):
    """Represent a new `Tag`, which is not yet stored in Paperless."""

    _api_path: ClassVar[str] = API_PATH["tags"]

    _create_required_fields: ClassVar[set[str]] = {
        "name",
        "color",
        "is_inbox_tag",
        "match",
        "matching_algorithm",
        "is_insensitive",
    }

    name: str | None = None
    color: str | None = None
    text_color: str | None = None
    is_inbox_tag: bool | None = None
    owner: int | None = None


class CorrespondentService(
    ServiceBase,
    services.SecurableMixin,
    services.CallableMixin[Correspondent],
    services.DraftableMixin[CorrespondentDraft],
    services.IterableMixin[Correspondent],
):
    """Represent a factory for Paperless `Correspondent` models."""

    _api_path = API_PATH["correspondents"]
    _resource = PaperlessResource.CORRESPONDENTS

    _draft_cls = CorrespondentDraft
    _resource_cls = Correspondent


class DocumentTypeService(
    ServiceBase,
    services.SecurableMixin,
    services.CallableMixin[DocumentType],
    services.DraftableMixin[DocumentTypeDraft],
    services.IterableMixin[DocumentType],
):
    """Represent a factory for Paperless `DocumentType` models."""

    _api_path = API_PATH["document_types"]
    _resource = PaperlessResource.DOCUMENT_TYPES

    _draft_cls = DocumentTypeDraft
    _resource_cls = DocumentType


class StoragePathService(
    ServiceBase,
    services.SecurableMixin,
    services.CallableMixin[StoragePath],
    services.DraftableMixin[StoragePathDraft],
    services.IterableMixin[StoragePath],
):
    """Represent a factory for Paperless `StoragePath` models."""

    _api_path = API_PATH["storage_paths"]
    _resource = PaperlessResource.STORAGE_PATHS

    _draft_cls = StoragePathDraft
    _resource_cls = StoragePath


class TagService(
    ServiceBase,
    services.SecurableMixin,
    services.CallableMixin[Tag],
    services.DraftableMixin[TagDraft],
    services.IterableMixin[Tag],
):
    """Represent a factory for Paperless `Tag` models."""

    _api_path = API_PATH["tags"]
    _resource = PaperlessResource.TAGS

    _draft_cls = TagDraft
    _resource_cls = Tag
