"""Provide `CustomField` related models and services."""

from typing import TYPE_CHECKING, Any, ClassVar, overload

from pypaperless.const import API_PATH, PaperlessResource

from .base import ServiceBase, PaperlessModel
from .common import (
    CUSTOM_FIELD_TYPE_VALUE_MAP,
    CustomFieldExtraData,
    CustomFieldType,
    CustomFieldValue,
    CustomFieldValueT,
)
from .mixins import services, models

if TYPE_CHECKING:
    from pypaperless import Paperless


class CustomField(
    PaperlessModel,
    models.UpdatableMixin,
    models.DeletableMixin,
):
    """Represent a Paperless `CustomField`."""

    _api_path: ClassVar[str] = API_PATH["custom_fields_single"]

    id: int
    name: str | None = None
    data_type: CustomFieldType | None = None
    extra_data: CustomFieldExtraData | None = None
    document_count: int | None = None

    def __init__(self, client: "Paperless", data: dict[str, Any], **kwargs: Any) -> None:
        """Initialize a `CustomField` instance."""
        super().__init__(client, data, **kwargs)
        self._format_api_path(data)

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
        cache = self._client.cache.custom_fields

        if cache and self.id in cache:
            klass = CUSTOM_FIELD_TYPE_VALUE_MAP.get(
                self.data_type or CustomFieldType.UNKNOWN, CustomFieldValue
            )
            klass_data = {
                "field": self.id,
                "value": value,
                "name": self.name,
                "data_type": self.data_type,
                "extra_data": self.extra_data,
            }
            return klass(**klass_data)

        return CustomFieldValue(field=self.id, value=value)


class CustomFieldDraft(PaperlessModel, models.CreatableMixin):
    """Represent a new Paperless `CustomField`, which is not stored in Paperless."""

    _api_path: ClassVar[str] = API_PATH["custom_fields"]

    _create_required_fields: ClassVar[set[str]] = {"name", "data_type"}

    name: str | None = None
    data_type: CustomFieldType | None = None
    extra_data: CustomFieldExtraData | None = None


class CustomFieldService(
    ServiceBase,
    services.CallableMixin[CustomField],
    services.DraftableMixin[CustomFieldDraft],
    services.IterableMixin[CustomField],
):
    """Represent a factory for Paperless `CustomField` models."""

    _api_path = API_PATH["custom_fields"]
    _resource = PaperlessResource.CUSTOM_FIELDS

    _draft_cls = CustomFieldDraft
    _resource_cls = CustomField
