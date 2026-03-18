"""Provide base classes for services."""

from typing import TYPE_CHECKING, Protocol

from pypaperless.const import API_PATH, PaperlessResource

if TYPE_CHECKING:
    from pypaperless import Paperless


class PaperlessService:
    """Base class for all services in PyPaperless."""

    def __init__(self, client: "Paperless") -> None:
        """Initialize a `PaperlessService` instance."""
        self._client = client


class ResourceServiceProtocol[ResourceT](Protocol):
    """Protocol for any `ResourceService` instances and its ancestors."""

    _client: "Paperless"
    _api_path: str
    _resource: PaperlessResource
    _resource_cls: type[ResourceT]


class ResourceService(PaperlessService):
    """Base class for all resource services in PyPaperless."""

    _api_path = API_PATH["index"]
    _resource: PaperlessResource

    @property
    def api_path(self) -> str:
        """Return the API path for the object."""
        return self._api_path
