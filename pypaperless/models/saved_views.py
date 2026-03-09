"""Provide `SavedView` related models."""

from typing import TYPE_CHECKING, Any, ClassVar

from pypaperless.const import API_PATH

from . import mixins
from .base import PaperlessModel
from .common import SavedViewFilterRuleType

if TYPE_CHECKING:
    from pypaperless import Paperless


class SavedView(PaperlessModel, mixins.SecurableMixin):
    """Represent a Paperless `SavedView`."""

    _api_path: ClassVar[str] = API_PATH["saved_views_single"]

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

    def __init__(self, client: "Paperless", data: dict[str, Any], **kwargs: Any) -> None:
        """Initialize a `SavedView` instance."""
        super().__init__(client, data, **kwargs)
        self._format_api_path(data)
