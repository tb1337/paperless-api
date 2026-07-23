"""Provide `SavedView` related models."""

import re
from enum import StrEnum
from typing import Annotated, ClassVar, Self

from pydantic import BaseModel, PlainValidator

from pypaperless.const import EndpointPath

from . import mixins
from .base import IdentifiedModel

_CUSTOM_FIELD_RE: re.Pattern[str] = re.compile(r"^custom_field_(\d+)$")


class SavedViewDisplayMode(StrEnum):
    """Represent a subtype of `SavedView`."""

    TABLE = "table"
    SMALL_CARDS = "smallCards"
    LARGE_CARDS = "largeCards"
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls, *_: object) -> Self:
        """Return the UNKNOWN member for any unrecognised value."""
        return cls["UNKNOWN"]


class SavedViewDisplayField(StrEnum):
    """Represent a subtype of `SavedView`."""

    TITLE = "title"
    CREATED = "created"
    ADDED = "added"
    TAGS = "tag"
    CORRESPONDENT = "correspondent"
    DOCUMENT_TYPE = "documenttype"
    STORAGE_PATH = "storagepath"
    NOTES = "notes"
    OWNER = "owner"
    SHARED = "shared"
    ASN = "asn"
    PAGE_COUNT = "pagecount"


class SavedViewCustomFieldDisplay(str):
    """Represent a dynamic custom-field column entry in :class:`SavedView`.

    Paperless-ngx encodes custom field columns as ``"custom_field_<pk>"``
    strings.  This class wraps such a value and exposes the numeric PK via
    the :attr:`pk` property while remaining a plain :class:`str` so it
    serialises transparently.

    Example::

        entry = SavedViewCustomFieldDisplay("custom_field_8")
        print(entry.pk)  # 8

    """

    __slots__ = ()

    def __new__(cls, value: str) -> Self:
        """Validate and intern the raw string value."""
        if not _CUSTOM_FIELD_RE.match(value):
            msg = f"Not a custom field display value: {value!r}"
            raise ValueError(msg)
        return super().__new__(cls, value)

    def __repr__(self) -> str:
        """Return repr(self)."""
        return f"SavedViewCustomFieldDisplay({super().__repr__()})"

    @property
    def pk(self) -> int:
        """Return the custom field PK encoded in this display value.

        Example::

            entry = SavedViewCustomFieldDisplay("custom_field_8")
            assert entry.pk == 8

        """
        return int(self[len("custom_field_") :])


def _coerce_display_field(v: object) -> "SavedViewDisplayField | SavedViewCustomFieldDisplay":
    """Try SavedViewDisplayField first, then SavedViewCustomFieldDisplay; raise on mismatch."""
    if isinstance(v, (SavedViewDisplayField, SavedViewCustomFieldDisplay)):
        return v
    if isinstance(v, str):
        try:
            return SavedViewDisplayField(v)
        except ValueError:
            pass
        return SavedViewCustomFieldDisplay(v)
    msg = f"Expected str, got {type(v).__name__!r}"
    raise ValueError(msg)


type _DisplayFieldValue = Annotated[
    SavedViewDisplayField | SavedViewCustomFieldDisplay,
    PlainValidator(_coerce_display_field),
]


class SavedViewFilterRule(BaseModel):
    """Represent a subtype of `SavedView`."""

    rule_type: int | None = None
    value: str | None = None


class SavedView(IdentifiedModel, mixins.SecurableModel):
    """Represent a Paperless `SavedView`."""

    _api_path: ClassVar[str] = EndpointPath.SAVED_VIEWS_SINGLE

    name: str | None = None
    sort_field: str | None = None
    sort_reverse: bool | None = None
    filter_rules: list[SavedViewFilterRule] | None = None
    page_size: int | None = None
    display_mode: SavedViewDisplayMode | None = None
    display_fields: list[_DisplayFieldValue] | None = None
