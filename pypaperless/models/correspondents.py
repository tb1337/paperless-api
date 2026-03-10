"""Provide `Correspondent` related models."""

import datetime
from typing import ClassVar

from pypaperless.const import API_PATH

from . import mixins
from .base import PaperlessModel


class Correspondent(
    PaperlessModel,
    mixins.MatchingFieldsMixin,
    mixins.SecurableMixin,
):
    """Represent a Paperless `Correspondent`."""

    _api_path: ClassVar[str] = API_PATH["correspondents_single"]

    id: int | None = None
    slug: str | None = None
    name: str | None = None
    document_count: int | None = None
    last_correspondence: datetime.date | None = None


class CorrespondentDraft(
    PaperlessModel,
    mixins.MatchingFieldsMixin,
    mixins.SecurableDraftMixin,
    mixins.CreatableMixin,
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
