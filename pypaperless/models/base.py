"""Provide base classes."""

from typing import TYPE_CHECKING, Any, ClassVar, Self, TypeVar, final

from pydantic import BaseModel, ConfigDict, PrivateAttr, model_serializer

from pypaperless.const import API_PATH
from pypaperless.utils import object_to_dict_value

if TYPE_CHECKING:
    from pypaperless import Paperless


ResourceT = TypeVar("ResourceT", bound="PaperlessModel")


class _PaperlessBase(BaseModel):
    """Internal base: binds ``_client`` from validation context and provides ``from_data``."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    _client: "Paperless" = PrivateAttr()

    def model_post_init(self, __context: Any, /) -> None:
        """Bind ``_client`` from validation context."""
        if isinstance(__context, dict) and "client" in __context:
            self._client = __context["client"]

    @classmethod
    def from_data(cls, client: "Paperless", data: Any, **context: Any) -> Self:
        """Return a new instance of ``cls`` from ``data``."""
        return cls.model_validate(data, context={"client": client, **context})


class PaperlessModel(_PaperlessBase):
    """Base class for all models in PyPaperless."""

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
        use_enum_values=False,
    )

    _api_path: ClassVar[str] = API_PATH["index"]
    _pk_field: ClassVar[str] = "id"

    _snapshot: dict[str, Any] = PrivateAttr(default_factory=dict)

    def model_post_init(self, __context: Any, /) -> None:
        """Bind `_client` from validation context and resolve the instance API path."""
        super().model_post_init(__context)
        pk = getattr(self, self._pk_field, None)
        if pk is not None:
            object.__setattr__(self, "_api_path", self._api_path.format(pk=pk))
        self._snapshot = self._build_snapshot()

    def _build_snapshot(self) -> dict[str, Any]:
        """Return the current field values as a serialized dict."""
        return {
            name: object_to_dict_value(getattr(self, name)) for name in self.__class__.model_fields
        }

    @classmethod
    def format_api_path(cls, **kwargs: Any) -> str:
        """Return the formatted API path for this model class."""
        return cls._api_path.format(**kwargs)

    @final
    @classmethod
    def from_data(
        cls,
        client: "Paperless",
        data: dict[str, Any],
        **_context: Any,
    ) -> Self:
        """Return a new instance of `cls` from `data`.

        Primarily used by service-level factory methods.
        """
        return cls.model_validate(data, context={"client": client})

    @property
    def api_path(self) -> str:
        """Return the API path for this model instance."""
        return self._api_path

    @property
    def snapshot(self) -> dict[str, Any]:
        """Return the serialized field state as of the last API sync."""
        return self._snapshot

    def refresh_from(self, data: dict[str, Any]) -> None:
        """Replace all field values and snapshot in-place from a fresh API response."""
        fresh = type(self).from_data(self._client, data)
        for name in self.__class__.model_fields:
            setattr(self, name, getattr(fresh, name))
        self._snapshot = self._build_snapshot()


class PaperlessCustomDataModel(_PaperlessBase):
    """Base class for all custom data types in PyPaperless."""

    _data: Any = PrivateAttr(default=None)

    def model_post_init(self, __context: Any, /) -> None:
        """Bind `_client` and `_data` from validation context."""
        super().model_post_init(__context)
        if isinstance(__context, dict) and "data" in __context:
            self._data = __context["data"]

    @classmethod
    def from_data(cls, client: "Paperless", data: Any, **_context: Any) -> Self:
        """Return a new instance of ``cls`` from API data."""
        return cls.model_validate({}, context={"client": client, "data": data})

    @property
    def data(self) -> Any:
        """Return the internal custom-model data payload."""
        return self._data

    @data.setter
    def data(self, value: Any) -> None:
        """Set the internal custom-model data payload."""
        self._data = value

    def serialize(self) -> Any:
        """Return the JSON-compatible payload for this model."""
        payload = {
            field_name: getattr(self, field_name) for field_name in self.__class__.model_fields
        }
        return object_to_dict_value(payload)

    @model_serializer(mode="plain")
    def _model_serializer(self) -> Any:
        """Delegate Pydantic serialization to the custom ``serialize`` method."""
        return self.serialize()
