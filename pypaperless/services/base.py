"""Provide base classes for services."""

from typing import TYPE_CHECKING, Protocol

from pypaperless.const import API_PATH, PaperlessResource

if TYPE_CHECKING:
    from pypaperless import Paperless


class PaperlessBase:
    """Superclass for all classes in PyPaperless."""

    _api_path = API_PATH["index"]

    def __init__(self, client: "Paperless") -> None:
        """Initialize a `PaperlessBase` instance."""
        self._client = client

    @property
    def api_path(self) -> str:
        """Return the API path for the object."""
        return self._api_path


class ServiceProtocol[ResourceT](Protocol):
    """Protocol for any `ServiceBase` instances and its ancestors."""

    _client: "Paperless"
    _api_path: str
    _resource: PaperlessResource
    _resource_cls: type[ResourceT]


class ServiceBase(PaperlessBase):
    """Base class for all services in PyPaperless."""

    _resource: PaperlessResource
