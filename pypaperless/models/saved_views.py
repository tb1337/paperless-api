"""Provide `SavedView` related models and helpers."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, final

from pypaperless.const import API_PATH, PaperlessResource

from .base import HelperBase, PaperlessModel
from .common import SavedViewFilterRuleType
from .mixins import helpers, models

if TYPE_CHECKING:
    from pypaperless import Paperless


@final
@dataclass(init=False)
class SavedView(
    PaperlessModel,
    models.PermissionFieldsMixin,
):  # pylint: disable=too-many-instance-attributes
    """Represent a Paperless `SavedView`."""

    _api_path = API_PATH["saved_views_single"]

    id: int | None = None
    name: str | None = None
    show_on_dashboard: bool | None = None
    show_in_sidebar: bool | None = None
    sort_field: str | None = None
    sort_reverse: bool | None = None
    filter_rules: list[SavedViewFilterRuleType] | None = None

    def __init__(self, api: "Paperless", data: dict[str, Any]):
        """Initialize a `SavedView` instance."""
        super().__init__(api, data)

        self._api_path = self._api_path.format(pk=data.get("id"))


@final
class SavedViewHelper(
    HelperBase[SavedView],
    helpers.CallableMixin[SavedView],
    helpers.IterableMixin[SavedView],
):
    """Represent a factory for Paperless `SavedView` models."""

    _api_path = API_PATH["saved_views"]
    _resource = PaperlessResource.SAVED_VIEWS

    _resource_cls = SavedView
