"""Provide base classes."""

from dataclasses import Field, dataclass, fields
from typing import TYPE_CHECKING, Any, Generic, Protocol, TypeVar, final

from pypaperless.const import API_PATH, PaperlessResource
from pypaperless.models.utils import dict_value_to_object

if TYPE_CHECKING:
    from pypaperless import Paperless


ResourceT = TypeVar("ResourceT", bound="PaperlessModel")


class PaperlessBase:
    """Superclass for all classes in PyPaperless."""

    _api_path = API_PATH["index"]

    def __init__(self, api: "Paperless"):
        """Initialize a `PaperlessBase` instance."""
        self._api = api


class HelperProtocol(Protocol, Generic[ResourceT]):
    """Protocol for any `HelperBase` instances and its ancestors."""

    _api: "Paperless"
    _api_path: str
    _resource: PaperlessResource
    _resource_cls: type[ResourceT]


class HelperBase(PaperlessBase, Generic[ResourceT]):
    """Base class for all helpers in PyPaperless."""

    _resource: PaperlessResource

    def __init__(self, api: "Paperless"):
        """Initialize a `HelperBase` instance."""
        super().__init__(api)

        self._api.local_resources.add(self._resource)

    @property
    def is_available(self) -> bool:
        """Return if the attached endpoint is available, or not."""
        return self._resource in self._api.remote_resources


@dataclass(init=False)
class PaperlessModelProtocol(Protocol):
    """Protocol for any `PaperlessBase` instances and its ancestors."""

    _api: "Paperless"
    _api_path: str
    _data: dict[str, Any]
    _fetched: bool
    _params: dict[str, Any]

    # fmt: off
    def _get_dataclass_fields(self) -> list[Field]: ...
    def _set_dataclass_fields(self) -> None: ...
    # fmt: on


@dataclass(init=False)
class PaperlessModel(PaperlessBase):
    """Base class for all models in PyPaperless."""

    def __init__(self, api: "Paperless", data: dict[str, Any]):
        """Initialize a `PaperlessModel` instance."""
        super().__init__(api)
        self._data = {}
        self._data.update(data)
        self._fetched = False
        self._params: dict[str, Any] = {}

    @final
    @classmethod
    def create_with_data(
        cls: type[ResourceT],
        api: "Paperless",
        data: dict[str, Any],
        fetched: bool = False,
    ) -> ResourceT:
        """Return a new instance of `cls` from `data`.

        Primarily used by class factories to create new model instances.

        Example: `document = Document.create_with_data(...)`
        """
        item = cls(api, data=data)
        item._fetched = fetched
        if fetched:
            item._set_dataclass_fields()
        return item

    @final
    def _get_dataclass_fields(self) -> list[Field]:
        """Get the dataclass fields."""
        return [
            field
            for field in fields(self)
            if (not field.name.startswith("_") or field.name == "__search_hit__")
        ]

    @final
    def _set_dataclass_fields(self) -> None:
        """Set the dataclass fields from `self._data`."""
        for field in self._get_dataclass_fields():
            value = dict_value_to_object(
                f"{self.__class__.__name__}.{field.name}",
                self._data.get(field.name),
                field.type,
                field.default,
                self._api,
            )
            setattr(self, field.name, value)

    async def load(self) -> None:
        """Get `model data` from DRF."""
        data = await self._api.request_json("get", self._api_path, params=self._params)

        self._data.update(data)
        self._set_dataclass_fields()
        self._fetched = True
