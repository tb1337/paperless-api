"""CreatableMixin for PyPaperless services."""

from typing import Any, Protocol

from pypaperless.exceptions import DraftNotSupportedError
from pypaperless.models.base import ResourceT
from pypaperless.services.base import ServiceProtocol


class _DraftLike(Protocol):
    """Protocol satisfied by all draft model classes (CreatableMixin + PaperlessModel)."""

    @property
    def api_path(self) -> str: ...

    def validate_draft(self) -> None: ...

    def serialize(self) -> dict[str, Any]: ...


class CreatableMixin(ServiceProtocol[ResourceT]):
    """Provide the `create` and `save` methods for PyPaperless services."""

    _draft_cls: type[ResourceT]

    def create(self, **kwargs: Any) -> ResourceT:
        """Return a fresh and empty `PaperlessModel` instance.

        Example:
        -------
        ```python
        draft = paperless.documents.create(document=bytes(...), title="New Document")
        # do something
        ```

        """
        if not hasattr(self, "_draft_cls"):
            message = "Service class has no _draft_cls attribute."
            raise DraftNotSupportedError(message)
        kwargs.update({"id": -1})

        return self._draft_cls.from_data(self._client, data=kwargs)

    async def save(self, draft: _DraftLike) -> int | str:
        """Create a new `resource item` in Paperless.

        Return the created item `id`, or a `task_id` in case of documents.

        Example:
        -------
        ```python
        draft = paperless.documents.create(document=bytes(...))
        draft.title = "Add a title"

        # request Paperless to store the new item
        await paperless.documents.save(draft)
        ```

        """
        draft.validate_draft()
        kwdict = draft.serialize()
        res = await self._client.request_json("post", draft.api_path, **kwdict)

        if isinstance(res, dict):
            return int(res["id"])
        return str(res)
