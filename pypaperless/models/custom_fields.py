"""Provide `CustomField` related models and helpers."""

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Any, final

from pypaperless.const import API_PATH

from .base import HelperBase, PaperlessModel
from .mixins import helpers, models

if TYPE_CHECKING:
    from pypaperless import Paperless


@final
class CustomFieldType(Enum):
    """Represent a subtype of `CustomField`."""

    STRING = "string"
    BOOLEAN = "boolean"
    INTEGER = "integer"
    FLOAT = "float"
    MONETARY = "monetary"
    DATE = "date"
    URL = "url"
    DOCUMENT_LINK = "documentlink"
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls: type, value: object) -> "CustomFieldType":  # noqa ARG003
        """Set default member on unknown value."""
        return CustomFieldType.UNKNOWN


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
@dataclass(kw_only=True)
class CustomFieldValueType:
    """Represent a subtype of `Document`."""

    field: int | None = None
    value: Any | None = None


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
