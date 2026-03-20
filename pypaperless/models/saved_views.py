"""Provide `SavedView` related models."""

from typing import ClassVar

from pydantic import BaseModel

from pypaperless.const import API_PATH

from . import mixins
from .base import PaperlessModel


class SavedViewFilterRule(BaseModel):
    """Represent a subtype of `SavedView`."""

    rule_type: int | None = None
    value: str | None = None


class SavedView(PaperlessModel, mixins.SecurableModel):
    """Represent a Paperless `SavedView`."""

    _api_path: ClassVar[str] = API_PATH["saved_views_single"]

    id: int | None = None
    name: str | None = None
    show_on_dashboard: bool | None = None
    show_in_sidebar: bool | None = None
    sort_field: str | None = None
    sort_reverse: bool | None = None
    filter_rules: list[SavedViewFilterRule] | None = None
    page_size: int | None = None
    display_mode: str | None = None
    display_fields: list[str] | None = None
