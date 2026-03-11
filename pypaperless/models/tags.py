"""Provide `Tag` related models."""

from typing import Any, ClassVar

from pydantic import field_validator

from pypaperless.const import API_PATH

from . import mixins
from .base import PaperlessModel


class Tag(
    PaperlessModel,
    mixins.MatchingFieldsMixin,
    mixins.SecurableMixin,
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

    @classmethod
    def _build_child_tag(cls, item: dict[str, Any]) -> "Tag":
        nested = [
            cls._build_child_tag(c) if isinstance(c, dict) else c
            for c in (item.get("children") or [])
        ]
        return cls.model_construct(**{**item, "children": nested or None})

    @field_validator("children", mode="before")
    @classmethod
    def _validate_children(cls, v: Any) -> Any:
        if not v:
            return v
        return [cls._build_child_tag(item) if isinstance(item, dict) else item for item in v]


class TagDraft(
    PaperlessModel,
    mixins.MatchingFieldsMixin,
    mixins.SecurableDraftMixin,
    mixins.CreatableMixin,
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
    parent: int | None = None
