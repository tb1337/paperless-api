"""Provide `Correspondent`, `DocumentType`, `StoragePath` and `Tag` related models and helpers."""

import datetime
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, final

from pypaperless.const import API_PATH

from .base import HelperBase, PaperlessModel
from .mixins import helpers, models

if TYPE_CHECKING:
    from pypaperless import Paperless


@final
@dataclass(init=False)
class Correspondent(  # pylint: disable=too-many-ancestors
    PaperlessModel,
    models.MatchingFieldsMixin,
    models.PermissionFieldsMixin,
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

    def __init__(self, api: "Paperless", data: dict[str, Any]):
        """Initialize a `Correspondent` instance."""
        super().__init__(api, data)

        self._api_path = self._api_path.format(pk=data.get("id"))


@final
@dataclass(init=False)
class CorrespondentDraft(
    PaperlessModel,
    models.MatchingFieldsMixin,
    models.CreatableMixin,
):
    """Represent a new Paperless `Correspondent`, which is not stored in Paperless."""

    _api_path = API_PATH["correspondents"]

    _create_required_fields = {"name", "match", "matching_algorithm", "is_insensitive"}

    name: str | None = None
    owner: int | None = None


@final
@dataclass(init=False)
class DocumentType(  # pylint: disable=too-many-ancestors
    PaperlessModel,
    models.MatchingFieldsMixin,
    models.PermissionFieldsMixin,
    models.UpdatableMixin,
    models.DeletableMixin,
):
    """Represent a Paperless `DocumentType`."""

    _api_path = API_PATH["document_types_single"]

    id: int | None = None
    slug: str | None = None
    name: str | None = None
    document_count: int | None = None

    def __init__(self, api: "Paperless", data: dict[str, Any]):
        """Initialize a `DocumentType` instance."""
        super().__init__(api, data)

        self._api_path = self._api_path.format(pk=data.get("id"))


@final
@dataclass(init=False)
class DocumentTypeDraft(
    PaperlessModel,
    models.MatchingFieldsMixin,
    models.CreatableMixin,
):
    """Represent a new Paperless `DocumentType`, which is not stored in Paperless."""

    _api_path = API_PATH["document_types"]

    _create_required_fields = {"name", "match", "matching_algorithm", "is_insensitive"}

    name: str | None = None
    owner: int | None = None


@final
@dataclass(init=False)
class StoragePath(  # pylint: disable=too-many-ancestors
    PaperlessModel,
    models.MatchingFieldsMixin,
    models.PermissionFieldsMixin,
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

    def __init__(self, api: "Paperless", data: dict[str, Any]):
        """Initialize a `StoragePath` instance."""
        super().__init__(api, data)

        self._api_path = self._api_path.format(pk=data.get("id"))


@final
@dataclass(init=False)
class StoragePathDraft(
    PaperlessModel,
    models.MatchingFieldsMixin,
    models.CreatableMixin,
):
    """Represent a new Paperless `StoragePath`, which is not stored in Paperless."""

    _api_path = API_PATH["storage_paths"]

    _create_required_fields = {"name", "path", "match", "matching_algorithm", "is_insensitive"}

    name: str | None = None
    path: str | None = None
    owner: int | None = None


@final
@dataclass(init=False)
class Tag(  # pylint: disable=too-many-ancestors,too-many-instance-attributes
    PaperlessModel,
    models.MatchingFieldsMixin,
    models.PermissionFieldsMixin,
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

    def __init__(self, api: "Paperless", data: dict[str, Any]):
        """Initialize a `Tag` instance."""
        super().__init__(api, data)

        self._api_path = self._api_path.format(pk=data.get("id"))


@final
@dataclass(init=False)
class TagDraft(
    PaperlessModel,
    models.MatchingFieldsMixin,
    models.CreatableMixin,
):
    """Represent a new Paperless `Tag`, which is not stored in Paperless."""

    _api_path = API_PATH["tags"]

    _create_required_fields = {
        "name",
        "color",
        "text_color",
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


@final
class CorrespondentHelper(  # pylint: disable=too-many-ancestors
    HelperBase[Correspondent],
    helpers.CallableMixin[Correspondent],
    helpers.DraftableMixin[CorrespondentDraft],
    helpers.IterableMixin[Correspondent],
):
    """Represent a factory for Paperless `Correspondent` models."""

    _api_path = API_PATH["correspondents"]

    _draft = CorrespondentDraft
    _resource = Correspondent


@final
class DocumentTypeHelper(  # pylint: disable=too-many-ancestors
    HelperBase[DocumentType],
    helpers.CallableMixin[DocumentType],
    helpers.DraftableMixin[DocumentTypeDraft],
    helpers.IterableMixin[DocumentType],
):
    """Represent a factory for Paperless `DocumentType` models."""

    _api_path = API_PATH["document_types"]

    _draft = DocumentTypeDraft
    _resource = DocumentType


@final
class StoragePathHelper(  # pylint: disable=too-many-ancestors
    HelperBase[StoragePath],
    helpers.CallableMixin[StoragePath],
    helpers.DraftableMixin[StoragePathDraft],
    helpers.IterableMixin[StoragePath],
):
    """Represent a factory for Paperless `StoragePath` models."""

    _api_path = API_PATH["storage_paths"]

    _draft = StoragePathDraft
    _resource = StoragePath


@final
class TagHelper(  # pylint: disable=too-many-ancestors
    HelperBase[Tag],
    helpers.CallableMixin[Tag],
    helpers.DraftableMixin[TagDraft],
    helpers.IterableMixin[Tag],
):
    """Represent a factory for Paperless `Tag` models."""

    _api_path = API_PATH["tags"]

    _draft = TagDraft
    _resource = Tag
