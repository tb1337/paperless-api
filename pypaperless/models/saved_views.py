"""Provide `SavedView` related models and helpers."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from pypaperless.const import API_PATH, PaperlessResource

from .base import HelperBase, PaperlessModel
from .common import SavedViewFilterRuleType
from .mixins import helpers, models

if TYPE_CHECKING:
    from pypaperless import Paperless


@dataclass(init=False)
class SavedView(
    PaperlessModel,
    models.SecurableMixin,
):
    """Represent a Paperless `SavedView`."""

    _api_path = API_PATH["saved_views_single"]

    id: int | None = None
    name: str | None = None
    show_on_dashboard: bool | None = None
    show_in_sidebar: bool | None = None
    sort_field: str | None = None
    sort_reverse: bool | None = None
    filter_rules: list[SavedViewFilterRuleType] | None = None
    page_size: int | None = None
    display_mode: str | None = None
    display_fields: list[str] | None = None

    def __init__(self, api: "Paperless", data: dict[str, Any]) -> None:
        """Initialize a `SavedView` instance."""
        super().__init__(api, data)

        self._api_path = self._api_path.format(pk=data.get("id"))


class SavedViewHelper(
    HelperBase[SavedView],
    helpers.CallableMixin[SavedView],
    helpers.IterableMixin[SavedView],
    helpers.SecurableMixin,
):
    """Represent a factory for Paperless `SavedView` models."""

    _api_path = API_PATH["saved_views"]
    _resource = PaperlessResource.SAVED_VIEWS

    _resource_cls = SavedView
