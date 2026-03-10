"""DraftableMixin for PyPaperless services."""

from typing import Any

from pypaperless.exceptions import DraftNotSupportedError
from pypaperless.models.base import ResourceT
from pypaperless.services.base import ServiceProtocol


class DraftableMixin(ServiceProtocol[ResourceT]):
    """Provide the `draft` and `save` methods for PyPaperless services."""

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
            message = "Service class has no _draft_cls attribute."
            raise DraftNotSupportedError(message)
        kwargs.update({"id": -1})

        return self._draft_cls.create_with_data(self._client, data=kwargs)

    async def save(self, draft: ResourceT) -> int | str:
        """Create a new `resource item` in Paperless.

        Return the created item `id`, or a `task_id` in case of documents.

        Example:
        -------
        ```python
        draft = paperless.documents.draft(document=bytes(...))
        draft.title = "Add a title"

        # request Paperless to store the new item
        await paperless.documents.save(draft)
        ```

        """
        draft.validate_draft()  # type: ignore[attr-defined]
        kwdict = draft.serialize()  # type: ignore[attr-defined]
        res = await self._client.request_json("post", draft.api_path, **kwdict)

        if isinstance(res, dict):
            return int(res["id"])
        return str(res)
