"""Provide `CustomField` related models and helpers."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, final

from pypaperless.const import API_PATH

from .base import HelperBase, PaperlessModel
from .common import CustomFieldType
from .mixins import helpers, models

if TYPE_CHECKING:
    from pypaperless import Paperless


@final
@dataclass(init=False)
class CustomField(
    PaperlessModel,
    models.UpdatableMixin,
    models.DeletableMixin,
):
    """Represent a Paperless `CustomField`."""

    _api_path = API_PATH["custom_fields_single"]

    id: int
    name: str | None = None
    data_type: CustomFieldType | None = None

    def __init__(self, api: "Paperless", data: dict[str, Any]):
        """Initialize a `Document` instance."""
        super().__init__(api, data)

        self._api_path = self._api_path.format(pk=data.get("id"))


@final
@dataclass(init=False)
class CustomFieldDraft(
    PaperlessModel,
    models.CreatableMixin,
):
    """Represent a new Paperless `CustomField`, which is not stored in Paperless."""

    _api_path = API_PATH["custom_fields"]

    _create_required_fields = {"name", "data_type"}

    name: str | None = None
    data_type: CustomFieldType | None = None


@final
class CustomFieldHelper(  # pylint: disable=too-many-ancestors
    HelperBase[CustomField],
    helpers.CallableMixin[CustomField],
    helpers.DraftableMixin[CustomFieldDraft],
    helpers.IterableMixin[CustomField],
):
    """Represent a factory for Paperless `CustomField` models."""

    _api_path = API_PATH["custom_fields"]

    _draft = CustomFieldDraft
    _resource = CustomField
