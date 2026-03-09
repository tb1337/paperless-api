"""Provide base classes."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, ClassVar, Self, TypeVar, final

from pydantic import BaseModel, ConfigDict, PrivateAttr, TypeAdapter

from pypaperless.const import API_PATH

if TYPE_CHECKING:
    from pypaperless import Paperless


ResourceT = TypeVar("ResourceT", bound="PaperlessModel")


class PaperlessModel(BaseModel):
    """Base class for all models in PyPaperless.

    Models are pure data containers. All API operations (load, save, update,
    delete) are handled by services.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
        use_enum_values=False,
    )

    _api_path: ClassVar[str] = API_PATH["index"]

    _client: "Paperless" = PrivateAttr()
    _data: dict[str, Any] = PrivateAttr(default_factory=dict)

    def __init__(self, client: "Paperless", data: dict[str, Any], **kwargs: Any) -> None:
        """Initialize a `PaperlessModel` instance."""
        super().__init__(**kwargs)
        self._client = client
        self._data = dict(data)

    def _format_api_path(self, data: dict[str, Any], **format_kwargs: Any) -> None:
        """Format the _api_path with instance data.

        This is a helper method to easily format paths like `/api/documents/{pk}/`.
        Subclasses should call this in their __init__ if they need custom path formatting.
        """
        format_kwargs.setdefault("pk", data.get("id") or data.get("document"))
        if format_kwargs["pk"] is not None:
            object.__setattr__(self, "_api_path", self._api_path.format(**format_kwargs))

    @classmethod
    def format_api_path(cls, **kwargs: Any) -> str:
        """Return the formatted API path for this model class."""
        return cls._api_path.format(**kwargs)

    @final
    @classmethod
    def create_with_data(
        cls,
        client: "Paperless",
        data: dict[str, Any],
    ) -> Self:
        """Return a new instance of `cls` from `data`.

        Primarily used by class factories to create new model instances.
        """
        return cls(client=client, data=data, **data)

    def apply_data(self) -> None:
        """Apply data from `self._data` to model fields.

        Used by services after update operations to refresh model state.
        """
        for field_name, field_info in self.__class__.model_fields.items():
            if field_name in self._data:
                value = self._data[field_name]
                if field_info.annotation is not None:
                    try:
                        adapter = self._get_type_adapter(field_name, field_info.annotation)
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


class PaperlessModelData(ABC):
    """Base class for all custom data types in PyPaperless."""

    @classmethod
    @abstractmethod
    def unserialize(cls, client: "Paperless", data: Any) -> Self:
        """Return a new instance of `cls` from `data`."""

    @abstractmethod
    def serialize(self) -> Any:
        """Serialize the class data."""
