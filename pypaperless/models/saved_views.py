"""Model for saved view resource."""

from dataclasses import dataclass

from .base import PaperlessModel


@dataclass(kw_only=True)
class SavedViewFilterRule(PaperlessModel):
    """Represent a saved view filter rule resource on the Paperless api."""

    rule_type: int | None = None
    value: str | None = None


@dataclass(kw_only=True)
class SavedView(PaperlessModel):  # pylint: disable=too-many-instance-attributes
    """Represent a saved view resource on the Paperless api."""

    id: int | None = None
    name: str | None = None
    show_on_dashboard: bool | None = None
    show_in_sidebar: bool | None = None
    sort_field: str | None = None
    sort_reverse: bool | None = None
    filter_rules: list[SavedViewFilterRule] | None = None
    owner: int | None = None
    user_can_change: bool | None = None
