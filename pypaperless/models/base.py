"""Provide base classes."""

from typing import TYPE_CHECKING, Any

from pypaperless.const import ResourceT

if TYPE_CHECKING:
    from pypaperless import Paperless


class PaperlessBase:
    """Superclass for all classes in PyPaperless."""

    def __init__(self, api: "Paperless"):
        """Initialize a `PaperlessBase` instance."""
        self._api = api


class PaperlessModel(PaperlessBase):
    """Base class for all models in PyPaperless."""

    api_path = ""

    def __getattr__(self, attribute: str) -> Any:
        """Get an attribute from `self._data`."""
        if attribute.startswith("_"):
            raise KeyError()
        return self._data.get(attribute, None)

    def __init__(self, api: "Paperless", _data: dict[str, Any] | None = None):
        """Initialize a `PaperlessModel` instance."""
        super().__init__(api)
        self._data = {}
        self._fetched = False

        if _data:
            self._data.update(_data)

    @classmethod
    def parse_from_data(cls: type[ResourceT], api: "Paperless", data: dict[str, Any]) -> ResourceT:
        """Return an instance of `cls` from `data`."""
        item = cls(api, _data=data)
        item._fetched = True
        return item

    async def load(self) -> None:
        """Request `model data` from DRF."""
        self._data = await self._api.request_json("get", self.api_path.format(pk=self.id))
        self._fetched = True
