"""Provide base classes."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, ClassVar, Protocol, Self, TypeVar, final

from pydantic import BaseModel, ConfigDict

from pypaperless.const import API_PATH, PaperlessResource

if TYPE_CHECKING:
    from pypaperless import Paperless


ResourceT = TypeVar("ResourceT", bound="PaperlessModel")


class PaperlessBase:
    """Superclass for all classes in PyPaperless."""

    _api_path = API_PATH["index"]

    def __init__(self, api: "Paperless") -> None:
        """Initialize a `PaperlessBase` instance."""
        self._api = api


class HelperProtocol[ResourceT](Protocol):
    """Protocol for any `HelperBase` instances and its ancestors."""

    _api: "Paperless"
    _api_path: str
    _resource: PaperlessResource
    _resource_cls: type[ResourceT]


class HelperBase(PaperlessBase):
    """Base class for all helpers in PyPaperless."""

    _resource: PaperlessResource


class PaperlessModelProtocol(Protocol):
    """Protocol for any `PaperlessModel` instances and its ancestors."""

    _api: "Paperless"
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

    _api: "Paperless"
    _api_path: ClassVar[str] = API_PATH["index"]
    _data: dict[str, Any] = {}
    _fetched: bool = False
    _params: dict[str, Any] = {}

    def __init__(self, api: "Paperless", data: dict[str, Any], **kwargs: Any) -> None:
        """Initialize a `PaperlessModel` instance."""
        super().__init__(**kwargs)

        self._api = api
        self._data = dict(data)
        self._fetched = False
        self._params = {}

    @final
    @classmethod
    def create_with_data(
        cls,
        api: "Paperless",
        data: dict[str, Any],
        *,
        fetched: bool = False,
    ) -> Self:
        """Return a new instance of `cls` from `data`.

        Primarily used by class factories to create new model instances.

        Example: `document = Document.create_with_data(...)`
        """
        item = cls(api=api, data=data, **data)

        item._fetched = fetched
        return item

    @property
    def is_fetched(self) -> bool:
        """Return whether the `model data` is fetched or not."""
        return self._fetched

    async def load(self) -> None:
        """Get `model data` from DRF."""
        data = await self._api.request_json("get", self._api_path, params=self._params)

        self._data.update(data)
        self._apply_data()
        self._fetched = True

    def _apply_data(self) -> None:
        """Apply data from `self._data` to model fields."""
        from pydantic import PydanticSchemaGenerationError, TypeAdapter

        for field_name, field_info in self.__class__.model_fields.items():
            if field_name in self._data:
                try:
                    adapter = TypeAdapter(field_info.annotation)
                    value = adapter.validate_python(self._data[field_name])
                except PydanticSchemaGenerationError:
                    value = self._data[field_name]
                setattr(self, field_name, value)


class PaperlessModelData(ABC):
    """Base class for all custom data types in PyPaperless."""

    @classmethod
    @abstractmethod
    def unserialize(cls, api: "Paperless", data: Any) -> Self:
        """Return a new instance of `cls` from `data`."""

    @abstractmethod
    def serialize(self) -> Any:
        """Serialize the class data."""
