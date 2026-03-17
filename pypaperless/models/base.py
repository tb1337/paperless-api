"""Provide base classes."""

from typing import TYPE_CHECKING, Any, ClassVar, Self, TypeVar, final

from pydantic import BaseModel, ConfigDict, PrivateAttr, TypeAdapter, model_serializer

from pypaperless.const import API_PATH
from pypaperless.utils import object_to_dict_value

if TYPE_CHECKING:
    from pypaperless import Paperless


ResourceT = TypeVar("ResourceT", bound="PaperlessModel")


class PaperlessModel(BaseModel):
    """Base class for all models in PyPaperless."""

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
        use_enum_values=False,
    )

    _api_path: ClassVar[str] = API_PATH["index"]
    _pk_field: ClassVar[str] = "id"

    _client: "Paperless" = PrivateAttr()
    _data: dict[str, Any] = PrivateAttr(default_factory=dict)

    @property
    def api_path(self) -> str:
        """Return the API path for this model instance."""
        return self._api_path

    @property
    def data(self) -> dict[str, Any]:
        """Return the internal model data dictionary."""
        return self._data

    @data.setter
    def data(self, value: dict[str, Any]) -> None:
        """Set the internal model data dictionary."""
        self._data = value

    def __init__(self, client: "Paperless", data: dict[str, Any], **kwargs: Any) -> None:
        """Initialize a `PaperlessModel` instance."""
        super().__init__(**kwargs)
        self._client = client
        self._data = dict(data)
        self._set_api_path(self._data)

    def _set_api_path(self, data: dict[str, Any], **format_kwargs: Any) -> None:
        """Set the instance's `_api_path` by resolving its `{pk}` placeholder.

        Uses `_pk_field` to determine which data key provides the primary key value.
        Override `_pk_field` on a subclass to use a different source field.
        """
        format_kwargs.setdefault("pk", data.get(self._pk_field))
        if format_kwargs["pk"] is not None:
            object.__setattr__(self, "_api_path", self._api_path.format(**format_kwargs))

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
    ) -> Self:
        """Return a new instance of `cls` from `data`.

        Primarily used by service-level factory methods.
        """
        return cls(client=client, data=data, **data)

    def apply_data(self) -> None:
        """Apply data from `self.data` to model fields.

        Used by services after update operations to refresh model state.
        """
        for field_name, field_info in self.__class__.model_fields.items():
            if field_name in self.data:
                value = self.data[field_name]
                if annotation := field_info.annotation:
                    try:
                        adapter = self._get_type_adapter(field_name, annotation)
                        value = adapter.validate_python(value)
                    except (ValueError, TypeError):
                        pass
                setattr(self, field_name, value)

    @classmethod
    def _get_type_adapter(cls, field_name: str, annotation: type) -> TypeAdapter:
        """Return a cached TypeAdapter for the given field."""
        cache_attr = "__type_adapters__"
        cache: dict[str, TypeAdapter] = getattr(cls, cache_attr, None) or {}
        if field_name not in cache:
            cache[field_name] = TypeAdapter(annotation)
            setattr(cls, cache_attr, cache)
        return cache[field_name]


class PaperlessCustomDataModel(BaseModel):
    """Base class for all custom data types in PyPaperless."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    _client: "Paperless" = PrivateAttr()
    _data: Any = PrivateAttr(default=None)

    @property
    def data(self) -> Any:
        """Return the internal custom-model data payload."""
        return self._data

    @data.setter
    def data(self, value: Any) -> None:
        """Set the internal custom-model data payload."""
        self._data = value

    def __init__(self, client: "Paperless", data: Any, **kwargs: Any) -> None:
        """Initialize a ``PaperlessCustomDataModel`` instance."""
        super().__init__(**kwargs)
        self._client = client
        self._data = data

    @classmethod
    def from_data(cls, client: "Paperless", data: Any) -> Self:
        """Return a new instance of ``cls`` from API data."""
        return cls(client=client, data=data)

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
