"""Provide `Correspondent`, `DocumentType`, `StoragePath` and `Tag` related models and helpers."""

import datetime
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from pypaperless.const import API_PATH, PaperlessResource

from .base import HelperBase, PaperlessModel
from .mixins import helpers, models

if TYPE_CHECKING:
    from pypaperless import Paperless


@dataclass(init=False)
class Correspondent(
    PaperlessModel,
    models.MatchingFieldsMixin,
    models.SecurableMixin,
    models.UpdatableMixin,
    models.DeletableMixin,
):
    """Represent a Paperless `Correspondent`."""

    _api_path = API_PATH["correspondents_single"]

    id: int | None = None
    slug: str | None = None
    name: str | None = None
    document_count: int | None = None
    last_correspondence: datetime.datetime | None = None

    def __init__(self, api: "Paperless", data: dict[str, Any]) -> None:
        """Initialize a `Correspondent` instance."""
        super().__init__(api, data)

        self._api_path = self._api_path.format(pk=data.get("id"))


@dataclass(init=False)
class CorrespondentDraft(
    PaperlessModel,
    models.MatchingFieldsMixin,
    models.SecurableDraftMixin,
    models.CreatableMixin,
):
    """Represent a new `Correspondent`, which is not yet stored in Paperless."""

    _api_path = API_PATH["correspondents"]

    _create_required_fields = {
        "name",
        "match",
        "matching_algorithm",
        "is_insensitive",
    }

    name: str | None = None


@dataclass(init=False)
class DocumentType(
    PaperlessModel,
    models.MatchingFieldsMixin,
    models.SecurableMixin,
    models.UpdatableMixin,
    models.DeletableMixin,
):
    """Represent a Paperless `DocumentType`."""

    _api_path = API_PATH["document_types_single"]

    id: int | None = None
    slug: str | None = None
    name: str | None = None
    document_count: int | None = None

    def __init__(self, api: "Paperless", data: dict[str, Any]) -> None:
        """Initialize a `DocumentType` instance."""
        super().__init__(api, data)

        self._api_path = self._api_path.format(pk=data.get("id"))


@dataclass(init=False)
class DocumentTypeDraft(
    PaperlessModel,
    models.MatchingFieldsMixin,
    models.SecurableDraftMixin,
    models.CreatableMixin,
):
    """Represent a new `DocumentType`, which is not yet stored in Paperless."""

    _api_path = API_PATH["document_types"]

    _create_required_fields = {
        "name",
        "match",
        "matching_algorithm",
        "is_insensitive",
    }

    name: str | None = None
    owner: int | None = None


@dataclass(init=False)
class StoragePath(
    PaperlessModel,
    models.MatchingFieldsMixin,
    models.SecurableMixin,
    models.UpdatableMixin,
    models.DeletableMixin,
):
    """Represent a Paperless `StoragePath`."""

    _api_path = API_PATH["storage_paths_single"]

    id: int | None = None
    slug: str | None = None
    name: str | None = None
    path: str | None = None
    document_count: int | None = None

    def __init__(self, api: "Paperless", data: dict[str, Any]) -> None:
        """Initialize a `StoragePath` instance."""
        super().__init__(api, data)

        self._api_path = self._api_path.format(pk=data.get("id"))


@dataclass(init=False)
class StoragePathDraft(
    PaperlessModel,
    models.MatchingFieldsMixin,
    models.SecurableDraftMixin,
    models.CreatableMixin,
):
    """Represent a new `StoragePath`, which is not yet stored in Paperless."""

    _api_path = API_PATH["storage_paths"]

    _create_required_fields = {
        "name",
        "path",
        "match",
        "matching_algorithm",
        "is_insensitive",
    }

    name: str | None = None
    path: str | None = None
    owner: int | None = None


@dataclass(init=False)
class Tag(
    PaperlessModel,
    models.MatchingFieldsMixin,
    models.SecurableMixin,
    models.UpdatableMixin,
    models.DeletableMixin,
):
    """Represent a Paperless `Tag`."""

    _api_path = API_PATH["tags_single"]

    id: int | None = None
    slug: str | None = None
    name: str | None = None
    color: str | None = None
    text_color: str | None = None
    is_inbox_tag: bool | None = None
    document_count: int | None = None

    def __init__(self, api: "Paperless", data: dict[str, Any]) -> None:
        """Initialize a `Tag` instance."""
        super().__init__(api, data)

        self._api_path = self._api_path.format(pk=data.get("id"))


@dataclass(init=False)
class TagDraft(
    PaperlessModel,
    models.MatchingFieldsMixin,
    models.SecurableDraftMixin,
    models.CreatableMixin,
):
    """Represent a new `Tag`, which is not yet stored in Paperless."""

    _api_path = API_PATH["tags"]

    _create_required_fields = {
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


class CorrespondentHelper(
    HelperBase[Correspondent],
    helpers.SecurableMixin,
    helpers.CallableMixin[Correspondent],
    helpers.DraftableMixin[CorrespondentDraft],
    helpers.IterableMixin[Correspondent],
):
    """Represent a factory for Paperless `Correspondent` models."""

    _api_path = API_PATH["correspondents"]
    _resource = PaperlessResource.CORRESPONDENTS

    _draft_cls = CorrespondentDraft
    _resource_cls = Correspondent


class DocumentTypeHelper(
    HelperBase[DocumentType],
    helpers.SecurableMixin,
    helpers.CallableMixin[DocumentType],
    helpers.DraftableMixin[DocumentTypeDraft],
    helpers.IterableMixin[DocumentType],
):
    """Represent a factory for Paperless `DocumentType` models."""

    _api_path = API_PATH["document_types"]
    _resource = PaperlessResource.DOCUMENT_TYPES

    _draft_cls = DocumentTypeDraft
    _resource_cls = DocumentType


class StoragePathHelper(
    HelperBase[StoragePath],
    helpers.SecurableMixin,
    helpers.CallableMixin[StoragePath],
    helpers.DraftableMixin[StoragePathDraft],
    helpers.IterableMixin[StoragePath],
):
    """Represent a factory for Paperless `StoragePath` models."""

    _api_path = API_PATH["storage_paths"]
    _resource = PaperlessResource.STORAGE_PATHS

    _draft_cls = StoragePathDraft
    _resource_cls = StoragePath


class TagHelper(
    HelperBase[Tag],
    helpers.SecurableMixin,
    helpers.CallableMixin[Tag],
    helpers.DraftableMixin[TagDraft],
    helpers.IterableMixin[Tag],
):
    """Represent a factory for Paperless `Tag` models."""

    _api_path = API_PATH["tags"]
    _resource = PaperlessResource.TAGS

    _draft_cls = TagDraft
    _resource_cls = Tag
