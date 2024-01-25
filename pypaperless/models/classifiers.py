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
@dataclass(kw_only=True)
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
class CorrespondentHelper(  # pylint: disable=too-many-ancestors
    HelperBase[Correspondent],
    helpers.CallableMixin[Correspondent],
    helpers.DraftableMixin[CorrespondentDraft],
    helpers.IterableMixin[Correspondent],
):
    """Represent a factory for Paperless `Correspondent` models."""

    _api_path = API_PATH["correspondents"]

    _resource = Correspondent
