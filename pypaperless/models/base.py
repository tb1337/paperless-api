"""Provide base classes."""

from typing import TYPE_CHECKING, Any, ClassVar, Protocol, Self, TypeVar, final

from pydantic import BaseModel, ConfigDict, PrivateAttr, model_serializer
from pydantic_core import to_jsonable_python

from pypaperless.const import EndpointPath

if TYPE_CHECKING:
    from pypaperless.runtime import PaperlessRuntime


ResourceT = TypeVar("ResourceT", bound="PaperlessModel")
IdentifiedT = TypeVar("IdentifiedT", bound="IdentifiedModel")


class DraftLike(Protocol):
    """Protocol satisfied by all draft model classes.

    Any object that exposes :attr:`api_path`, :meth:`validate_draft`, and
    :meth:`serialize` is a valid draft that can be passed to
    :meth:`~pypaperless.client.PaperlessClient.save`.
    """

    @property
    def api_path(self) -> str:
        """Return the API path for this draft."""
        ...

    def validate_draft(self) -> None:
        """Raise if required fields are missing."""
        ...

    def serialize(self) -> dict[str, Any]:
        """Return a serialized representation suitable for the API."""
        ...


class _PaperlessBase(BaseModel):
    """Internal base: binds ``_runtime`` from validation context and provides ``from_data``."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    _runtime: "PaperlessRuntime" = PrivateAttr()

    def model_post_init(self, __context: Any, /) -> None:
        """Bind ``_runtime`` from validation context."""
        if isinstance(__context, dict) and "runtime" in __context:
            self._runtime = __context["runtime"]

    @classmethod
    def from_data(cls, runtime: "PaperlessRuntime", data: Any, **context: Any) -> Self:
        """Return a new instance of ``cls`` from ``data``."""
        return cls.model_validate(data, context={"runtime": runtime, **context})


class PaperlessModel(_PaperlessBase):
    """Base class for all models in PyPaperless."""

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
        use_enum_values=False,
        validate_assignment=True,
    )

    _api_path: ClassVar[str] = EndpointPath.INDEX
    _pk_field: ClassVar[str] = "id"
    _dump_exclude: ClassVar[set[str]] = set()

    _snapshot: dict[str, Any] = PrivateAttr(default_factory=dict)

    def model_post_init(self, __context: Any, /) -> None:
        """Bind `_runtime` from validation context and resolve the instance API path."""
        super().model_post_init(__context)
        pk = getattr(self, self._pk_field, None)
        if pk is not None:
            object.__setattr__(self, "_api_path", self._api_path.format(pk=pk))
        self._snapshot = self.api_dump()

    def api_dump(self) -> dict[str, Any]:
        """Return the JSON-safe field state as it is sent to the Paperless API.

        Keys are the API field names (aliases), fields marked ``exclude=True``
        and binary payload fields listed in ``_dump_exclude`` are omitted.

        Example::

            document = await paperless.documents(42)
            payload = document.api_dump()
            print(payload["title"])

        """
        return self.model_dump(mode="json", by_alias=True, exclude=self._dump_exclude or None)

    @classmethod
    def format_api_path(cls, **kwargs: Any) -> str:
        """Return the formatted API path for this model class."""
        return cls._api_path.format(**kwargs)

    @final
    @classmethod
    def from_data(
        cls,
        runtime: "PaperlessRuntime",
        data: dict[str, Any],
        **_context: Any,
    ) -> Self:
        """Return a new instance of `cls` from `data`.

        Primarily used by service-level factory methods.
        """
        return cls.model_validate(data, context={"runtime": runtime})

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
        fresh = type(self).from_data(self._runtime, data)
        for name in self.__class__.model_fields:
            setattr(self, name, getattr(fresh, name))
        self._snapshot = self.api_dump()


class IdentifiedModel(PaperlessModel):
    """Base class for models whose API endpoint always provides an ``id``.

    Subclasses expose ``id`` as a required, non-optional ``int``.
    """

    id: int


class PaperlessCustomDataModel(_PaperlessBase):
    """Base class for all custom data types in PyPaperless."""

    _data: Any = PrivateAttr(default=None)

    def model_post_init(self, __context: Any, /) -> None:
        """Bind `_runtime` and `_data` from validation context."""
        super().model_post_init(__context)
        if isinstance(__context, dict) and "data" in __context:
            self._data = __context["data"]

    @classmethod
    def from_data(cls, runtime: "PaperlessRuntime", data: Any, **_context: Any) -> Self:
        """Return a new instance of ``cls`` from API data."""
        return cls.model_validate({}, context={"runtime": runtime, "data": data})

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
        return to_jsonable_python(payload)

    @model_serializer(mode="plain")
    def _model_serializer(self) -> Any:
        """Delegate Pydantic serialization to the custom ``serialize`` method."""
        return self.serialize()
