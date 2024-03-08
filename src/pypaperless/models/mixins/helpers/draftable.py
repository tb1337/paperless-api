"""DraftableMixin for PyPaperless helpers."""

from typing import Any

from pypaperless.exceptions import DraftNotSupportedError
from pypaperless.models.base import HelperProtocol, ResourceT


class DraftableMixin(HelperProtocol[ResourceT]):
    """Provide the `draft` method for PyPaperless helpers."""

    _draft_cls: type[ResourceT]

    def draft(self, **kwargs: Any) -> ResourceT:
        """Return a fresh and empty `PaperlessModel` instance.

        Example:
        -------
        ```python
        draft = paperless.documents.draft(document=bytes(...), title="New Document")
        # do something
        ```

        """
        if not hasattr(self, "_draft_cls"):
            message = "Helper class has no _draft_cls attribute."
            raise DraftNotSupportedError(message)
        kwargs.update({"id": -1})

        return self._draft_cls.create_with_data(self._api, data=kwargs, fetched=True)
