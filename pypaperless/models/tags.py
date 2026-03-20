"""Provide `Tag` related models."""

from typing import ClassVar

from pypaperless.const import API_PATH, PaperlessResource

from . import mixins
from .base import PaperlessModel


class Tag(
    PaperlessModel,
    mixins.MatchingFieldsModel,
    mixins.SecurableModel,
    mixins.UpdatableModel,
    mixins.DeletableModel,
):
    """Represent a Paperless `Tag`."""

    _api_path: ClassVar[str] = API_PATH["tags_single"]
    _resource: ClassVar[PaperlessResource] = PaperlessResource.TAGS

    id: int | None = None
    slug: str | None = None
    name: str | None = None
    color: str | None = None
    text_color: str | None = None
    is_inbox_tag: bool | None = None
    document_count: int | None = None
    parent: int | None = None
    children: list["Tag"] | None = None


class TagDraft(
    PaperlessModel,
    mixins.MatchingFieldsModel,
    mixins.SecurableDraftModel,
    mixins.CreatableModel,
    mixins.SaveableModel,
):
    """Represent a new `Tag`, which is not yet stored in Paperless."""

    _api_path: ClassVar[str] = API_PATH["tags"]
    _resource: ClassVar[PaperlessResource] = PaperlessResource.TAGS

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
    parent: int | None = None
