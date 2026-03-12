"""Provide `CustomField` related models."""

import contextlib
import datetime
import re
from enum import Enum
from typing import Any, ClassVar, TypeVar, overload

from pydantic import BaseModel, Field, field_validator

from pypaperless.const import API_PATH

from . import mixins
from .base import PaperlessModel


class CustomFieldSelectOptions(BaseModel):
    """Represent the `extra_data.select_options` field of a `CustomField`."""

    id: str | None = None
    label: str | None = None


class CustomFieldExtraData(BaseModel):
    """Represent the `extra_data` field of a `CustomField`."""

    default_currency: str | None = None
    select_options: list[CustomFieldSelectOptions | None] = Field(default_factory=list)


class CustomFieldType(Enum):
    """Represent a subtype of `CustomField`."""

    STRING = "string"
    URL = "url"
    DATE = "date"
    BOOLEAN = "boolean"
    INTEGER = "integer"
    FLOAT = "float"
    MONETARY = "monetary"
    DOCUMENT_LINK = "documentlink"
    SELECT = "select"
    LONGTEXT = "longtext"
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls: type, *_: object) -> "CustomFieldType":
        """Set default member on unknown value."""
        return CustomFieldType.UNKNOWN


class CustomFieldValue(BaseModel):
    """Represent a subtype of `CustomField`."""

    field: int | None = None
    value: Any | None = None
    name: str | None = None
    data_type: CustomFieldType | None = None
    extra_data: CustomFieldExtraData | None = None


CustomFieldValueT = TypeVar("CustomFieldValueT", bound=CustomFieldValue)


class CustomFieldBooleanValue(CustomFieldValue):
    """Represent a boolean `CustomFieldValue`."""

    value: bool | None = None


class CustomFieldDateValue(CustomFieldValue):
    """Represent a date `CustomFieldValue`."""

    value: datetime.date | str | None = None

    @field_validator("value", mode="before")
    @classmethod
    def _parse_date(cls, v: datetime.date | str | None) -> datetime.date | str | None:
        """Convert the value to a date."""
        if isinstance(v, str):
            with contextlib.suppress(ValueError):
                dt = datetime.datetime.fromisoformat(v)
                return dt.date()
        return v


class CustomFieldDocumentLinkValue(CustomFieldValue):
    """Represent a document link `CustomFieldValue`."""

    value: list[int] | int | None = None


class CustomFieldFloatValue(CustomFieldValue):
    """Represent a float `CustomFieldValue`."""

    value: float | None = None


class CustomFieldIntegerValue(CustomFieldValue):
    """Represent an integer `CustomFieldValue`."""

    value: int | None = None


class CustomFieldMonetaryValue(CustomFieldValue):
    """Represent a monetary `CustomFieldValue`."""

    value: str | None = None

    @field_validator("value", mode="before")
    @classmethod
    def _coerce_value_to_str(cls, v: Any) -> str | None:
        if v is None:
            return None
        return str(v)

    @property
    def currency(self) -> str | None:
        """Return the currency of the `value` field."""
        if self.value and (match := re.match(r"^([a-zA-Z]{3})", self.value)):
            return match.group(1) if match else self.value
        if self.extra_data and self.extra_data.default_currency:
            return self.extra_data.default_currency
        return ""

    @currency.setter
    def currency(self, new_currency: str) -> None:
        """Override the currency of the field."""
        value = self.value or ""
        value = re.sub(r"^[a-zA-Z]{3}", "", value)

        if new_currency and re.match(r"^[A-Z]{3}$", new_currency):
            self.value = f"{new_currency}{value}"
        else:
            self.value = value

    @property
    def amount(self) -> float | None:
        """Return the amount without currentcy of the `value` field."""
        if self.value:
            numeric = re.sub(r"[^\d.]", "", self.value)
            return float(numeric)
        return None

    @amount.setter
    def amount(self, new_amount: float) -> None:
        """Set a new amount and construct the internal needed value."""
        self.value = f"{self.currency}{new_amount:.2f}"


class CustomFieldSelectValue(CustomFieldValue):
    """Represent a select `CustomFieldValue`."""

    value: int | str | None = None

    @property
    def labels(self) -> list[CustomFieldSelectOptions | None]:
        """Return the list of labels of the `CustomField`."""
        if not self.extra_data:
            return []
        return self.extra_data.select_options

    @property
    def label(self) -> str | None:
        """Return the label for `value` or fall back to `None`."""
        for opt in self.labels:
            if opt and opt.id == self.value:
                return opt.label
        return None


class CustomFieldStringValue(CustomFieldValue):
    """Represent a string `CustomFieldValue`."""

    value: str | None = None


class CustomFieldURLValue(CustomFieldValue):
    """Represent an url `CustomFieldValue`."""

    value: str | None = None


CUSTOM_FIELD_TYPE_VALUE_MAP: dict[CustomFieldType, type[CustomFieldValue]] = {
    CustomFieldType.BOOLEAN: CustomFieldBooleanValue,
    CustomFieldType.DATE: CustomFieldDateValue,
    CustomFieldType.DOCUMENT_LINK: CustomFieldDocumentLinkValue,
    CustomFieldType.FLOAT: CustomFieldFloatValue,
    CustomFieldType.INTEGER: CustomFieldIntegerValue,
    CustomFieldType.LONGTEXT: CustomFieldStringValue,
    CustomFieldType.MONETARY: CustomFieldMonetaryValue,
    CustomFieldType.SELECT: CustomFieldSelectValue,
    CustomFieldType.STRING: CustomFieldStringValue,
    CustomFieldType.URL: CustomFieldURLValue,
}


class CustomField(
    PaperlessModel,
):
    """Represent a Paperless `CustomField`."""

    _api_path: ClassVar[str] = API_PATH["custom_fields_single"]

    id: int
    name: str | None = None
    data_type: CustomFieldType | None = None
    extra_data: CustomFieldExtraData | None = None
    document_count: int | None = None

    @overload
    def draft_value(self, value: Any) -> CustomFieldValue: ...

    @overload
    def draft_value(
        self, value: Any, expected_type: type[CustomFieldValueT]
    ) -> CustomFieldValueT: ...

    def draft_value(
        self,
        value: Any,
        expected_type: type[CustomFieldValueT] | None = None,  # noqa: ARG002
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


class CustomFieldDraft(PaperlessModel, mixins.CreatableMixin):
    """Represent a new Paperless `CustomField`, which is not stored in Paperless."""

    _api_path: ClassVar[str] = API_PATH["custom_fields"]

    _create_required_fields: ClassVar[set[str]] = {"name", "data_type"}

    name: str | None = None
    data_type: CustomFieldType | None = None
    extra_data: CustomFieldExtraData | None = None
