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
        payload: dict[str, Any] = {}
        for field_name, value in item.items():
            if field_name == "children":
                continue
            field_info = cls.model_fields.get(field_name)
            if field_info is None or field_info.annotation is None:
                payload[field_name] = value
                continue
            try:
                payload[field_name] = cls._get_type_adapter(
                    field_name,
                    field_info.annotation,
                ).validate_python(value)
            except (ValueError, TypeError):
                payload[field_name] = value

        return cls.model_construct(
            **{
                **payload,
                "children": nested or None,
            }
        )

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
