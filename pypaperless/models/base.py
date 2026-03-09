"""Provide base classes."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, ClassVar, Protocol, Self, TypeVar, final

from pydantic import BaseModel, ConfigDict, PrivateAttr

from pypaperless.const import API_PATH, PaperlessResource

if TYPE_CHECKING:
    from pypaperless import Paperless


ResourceT = TypeVar("ResourceT", bound="PaperlessModel")


class PaperlessBase:
    """Superclass for all classes in PyPaperless."""

    _api_path = API_PATH["index"]

    def __init__(self, client: "Paperless") -> None:
        """Initialize a `PaperlessBase` instance."""
        self._client = client


class ServiceProtocol[ResourceT](Protocol):
    """Protocol for any `ServiceBase` instances and its ancestors."""

    _client: "Paperless"
    _api_path: str
    _resource: PaperlessResource
    _resource_cls: type[ResourceT]


class ServiceBase(PaperlessBase):
    """Base class for all services in PyPaperless."""

    _resource: PaperlessResource


class PaperlessModelProtocol(Protocol):
    """Protocol for any `PaperlessModel` instances and its ancestors."""

    _client: "Paperless"
    _api_path: str
    _data: dict[str, Any]
    _fetched: bool
    _params: dict[str, Any]

    # fmt: off
    def model_fields_set(self) -> set[str]: ...
    # fmt: on


class PaperlessModel(BaseModel):
    """Base class for all models in PyPaperless."""

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
        use_enum_values=False,
    )

    _api_path: ClassVar[str] = API_PATH["index"]

    # Private attributes - not part of the Pydantic model schema
    _client: "Paperless" = PrivateAttr()
    _data: dict[str, Any] = PrivateAttr(default_factory=dict)
    _fetched: bool = PrivateAttr(default=False)
    _params: dict[str, Any] = PrivateAttr(default_factory=dict)

    def __init__(self, client: "Paperless", data: dict[str, Any], **kwargs: Any) -> None:
        """Initialize a `PaperlessModel` instance."""
        super().__init__(**kwargs)
        self._client = client
        self._data = dict(data)
        self._fetched = False
        self._params = {}

    def _format_api_path(self, data: dict[str, Any], **format_kwargs: Any) -> None:
        """Format the _api_path with instance data.

        This is a helper method to easily format paths like `/api/documents/{pk}/`.
        Subclasses should call this in their __init__ if they need custom path formatting.

        Args:
            data: The raw data dictionary from API initialization.
            **format_kwargs: Additional keyword arguments for format() call.
                If not provided, 'pk' defaults to data['id'] and falls back to data['document'].

        Example:
            class Document(PaperlessModel):
                def __init__(self, client, data, **kwargs):
                    super().__init__(client, data, **kwargs)
                    self._format_api_path(data)

        """
        format_kwargs.setdefault("pk", data.get("id") or data.get("document"))
        if format_kwargs["pk"] is not None:
            object.__setattr__(self, "_api_path", self._api_path.format(**format_kwargs))

    @final
    @classmethod
    def create_with_data(
        cls,
        client: "Paperless",
        data: dict[str, Any],
        *,
        fetched: bool = False,
    ) -> Self:
        """Return a new instance of `cls` from `data`.

        Primarily used by class factories to create new model instances.

        Example: `document = Document.create_with_data(...)`
        """
        item = cls(client=client, data=data, **data)

        item._fetched = fetched
        return item

    @property
    def is_fetched(self) -> bool:
        """Return whether the `model data` is fetched or not."""
        return self._fetched

    async def load(self) -> None:
        """Get `model data` from DRF."""
        data = await self._client.request_json("get", self._api_path, params=self._params)

        self._data.update(data)
        self._apply_data()
        self._fetched = True

    def _apply_data(self) -> None:
        """Apply data from `self._data` to model fields.

        Uses Pydantic's model_construct for field-level type coercion
        without triggering full __init__ or validation overhead.
        """
        for field_name, field_info in self.__class__.model_fields.items():
            if field_name in self._data:
                value = self._data[field_name]
                if field_info.annotation is not None:
                    try:
                        adapter = self._get_type_adapter(field_name, field_info.annotation)
                        value = adapter.validate_python(value)
                    except Exception:  # noqa: BLE001
                        pass
                setattr(self, field_name, value)

    @classmethod
    def _get_type_adapter(cls, field_name: str, annotation: type) -> "TypeAdapter":
        """Return a cached TypeAdapter for the given field.

        Caches adapters per class to avoid re-creating them on every call.
        """
        from pydantic import TypeAdapter

        cache_attr = "__type_adapters__"
        cache: dict[str, TypeAdapter] = getattr(cls, cache_attr, None) or {}  # type: ignore[assignment]
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
