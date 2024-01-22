"""Provide the FactoryBase class."""

from typing import TYPE_CHECKING, Generic, Protocol

from pypaperless.models.base import PaperlessBase, ResourceT

if TYPE_CHECKING:
    from pypaperless import Paperless


class HelperProtocol(Protocol, Generic[ResourceT]):
    """Protocol for any `HelperBase` instances and its ancestors."""

    _api: "Paperless"
    _api_path: str
    _resource: type[ResourceT]


class HelperBase(PaperlessBase, Generic[ResourceT]):
    """Base class for all helpers in PyPaperless."""

    def __init__(self, api: "Paperless"):
        """Initialize a `HelperBase` instance."""
        super().__init__(api)

        # TODO: implement basic fetch
