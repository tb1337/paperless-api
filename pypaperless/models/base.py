"""Provide the PaperlessBase superclass."""

from typing import TYPE_CHECKING, Any

from pypaperless.const import ResourceT

if TYPE_CHECKING:
    from pypaperless import Paperless


class PaperlessBase:
    """Superclass for all models in PyPaperless."""

    @classmethod
    def parse(cls: type[ResourceT], data: dict[str, Any], api: "Paperless") -> ResourceT:
        """Return an instance of `cls` from `data`."""
        return cls(api, _data=data)

    def __getattr__(self, attribute: str) -> Any:
        """Getattr."""
        if attribute.startswith("_"):
            raise KeyError()
        if attribute not in self._data:
            raise KeyError()
        return self._data.get(attribute)

    def __init__(self, api: "Paperless", _data: dict[str, Any] | None = None):
        """Initialize a `PaperlessBase` instance."""
        self._api = api
        self._data = {}
        self._fetched = False

        if _data:
            self._data.update(_data)
