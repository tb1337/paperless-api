"""DraftableMixin for PyPaperless helpers."""

from typing import Any, final

from pypaperless.errors import DraftNotSupported
from pypaperless.models.base import HelperProtocol, ResourceT


class DraftableMixin(HelperProtocol[ResourceT]):  # pylint: disable=too-few-public-methods
    """Provide the `draft` method for PyPaperless helpers."""

    _draft: type[ResourceT]

    @final
    def draft(self, **kwargs: Any) -> ResourceT:
        """Return a fresh and empty `PaperlessModel` instance.

        Example:
        ```python
        draft = paperless.documents.draft(document=bytes(...), title="New Document")
        # do something
        ```
        """
        if not hasattr(self, "_draft"):
            raise DraftNotSupported("Helper class has no _draft attribute.")
        kwargs.update({"id": -1})

        return self._draft.create_with_data(self._api, data=kwargs, fetched=True)
