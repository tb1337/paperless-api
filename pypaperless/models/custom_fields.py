"""Provide `CustomField` related models and helpers."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, overload

from pypaperless.const import API_PATH, PaperlessResource

from .base import HelperBase, PaperlessModel
from .common import (
    CUSTOM_FIELD_TYPE_VALUE_MAP,
    CustomFieldExtraData,
    CustomFieldType,
    CustomFieldValue,
    CustomFieldValueT,
)
from .mixins import helpers, models

if TYPE_CHECKING:
    from pypaperless import Paperless


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
    extra_data: CustomFieldExtraData | None = None
    document_count: int | None = None

    def __init__(self, api: "Paperless", data: dict[str, Any]) -> None:
        """Initialize a `Document` instance."""
        super().__init__(api, data)

        self._api_path = self._api_path.format(pk=data.get("id"))

    @overload
    def draft_value(self, value: Any) -> CustomFieldValue: ...

    @overload
    def draft_value(
        self, value: Any, expected_type: type[CustomFieldValueT]
    ) -> CustomFieldValueT: ...

    def draft_value(
        self,
        value: Any,
        expected_type: type[CustomFieldValueT] | None = None,  # noqa: ARG002 # pylint: disable=unused-argument
    ) -> CustomFieldValue | CustomFieldValueT:
        """Draft a new `CustomFieldValue` instance."""
        cache = self._api.cache.custom_fields

        if cache and self.id in cache:
            klass = CUSTOM_FIELD_TYPE_VALUE_MAP.get(
                self.data_type or CustomFieldType.UNKNOWN, CustomFieldValue
            )
            return klass(field=self.id, value=value)

        return CustomFieldValue(field=self.id, value=value)


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
    extra_data: CustomFieldExtraData | None = None


class CustomFieldHelper(
    HelperBase[CustomField],
    helpers.CallableMixin[CustomField],
    helpers.DraftableMixin[CustomFieldDraft],
    helpers.IterableMixin[CustomField],
):
    """Represent a factory for Paperless `CustomField` models."""

    _api_path = API_PATH["custom_fields"]
    _resource = PaperlessResource.CUSTOM_FIELDS

    _draft_cls = CustomFieldDraft
    _resource_cls = CustomField
