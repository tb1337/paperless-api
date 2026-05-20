"""Provide base classes for services."""

from typing import TYPE_CHECKING, Protocol

from pypaperless.const import EndpointPath

if TYPE_CHECKING:
    from pypaperless.runtime import PaperlessRuntime


class PaperlessService:
    """Base class for all services in PyPaperless."""

    def __init__(self, runtime: "PaperlessRuntime") -> None:
        """Initialize a `PaperlessService` instance."""
        self._runtime = runtime


class ResourceServiceProtocol[ResourceT](Protocol):
    """Protocol capturing the minimum interface required by all resource service mixins."""

    _runtime: "PaperlessRuntime"
    _api_path: str
    _resource_cls: type[ResourceT]


class ResourceService(PaperlessService):
    """Base class for all resource services in PyPaperless."""

    _api_path = EndpointPath.INDEX

    @property
    def api_path(self) -> str:
        """Return the API path for the object."""
        return self._api_path
