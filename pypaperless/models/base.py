"""Provide base classes."""

from typing import TYPE_CHECKING, Any, Generic, Protocol, TypeVar, final

from pypaperless.const import API_PATH

if TYPE_CHECKING:
    from pypaperless import Paperless

ResourceT = TypeVar("ResourceT", bound="PaperlessModel")


class PaperlessModelProtocol(Protocol, Generic[ResourceT]):
    """Protocol for any `PaperlessBase` instances and its ancestors."""

    _api: "Paperless"
    _api_path: str
    _data: dict[str, Any]
    _fetched: bool
    _resource: type[ResourceT]

    @property
    def api_path(self) -> str:  # noqa
        ...


class PaperlessBase:
    """Superclass for all classes in PyPaperless."""

    _api_path = API_PATH["index"]

    def __init__(self, api: "Paperless"):
        """Initialize a `PaperlessBase` instance."""
        self._api = api

    @property
    def api_path(self) -> str:
        """Return the api path."""
        return self._api_path


class PaperlessModel(PaperlessBase):
    """Base class for all models in PyPaperless."""

    def __getattr__(self, attribute: str) -> Any:
        """Get an attribute from `PaperlessModel`."""
        return self._data.get(attribute, None)

    def __init__(self, api: "Paperless", data: dict[str, Any]):
        """Initialize a `PaperlessModel` instance."""
        super().__init__(api)
        self._data = {}
        self._fetched = False

        self._data.update(data)

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
        # if fetched:
        #     item._set_dataclass_fields()
        return item

    # @final
    # def _set_dataclass_fields(self) -> None:
    #     """Set the dataclass fields from `self._data`."""
    #     if not dataclasses.is_dataclass(self):
    #         raise ValueError("Class is no dataclass.")

    #     for field in dataclasses.fields(self):
    #         value = dict_value_to_object(
    #             f"{self.__class__.__name__}.{field.name}",
    #             self._data.get(field.name),  # type: ignore[union-attr]
    #             field.type,
    #             field.default,
    #         )
    #         setattr(self, field.name, value)

    @final
    async def load(self) -> None:
        """Get `model data` from DRF."""
        self._data = await self._api.request_json("get", self.api_path.format(pk=self.id))
        # self._set_dataclass_fields()
        self._fetched = True
