"""CreatableService for PyPaperless services."""

from typing import Any, Protocol

from pypaperless.exceptions import DraftNotSupportedError
from pypaperless.models.base import ResourceT
from pypaperless.services.base import ResourceServiceProtocol


class _DraftLike(Protocol):
    """Protocol satisfied by all draft model classes (CreatableModel + PaperlessModel)."""

    @property
    def api_path(self) -> str: ...

    def validate_draft(self) -> None: ...

    def serialize(self) -> dict[str, Any]: ...


class CreatableService(ResourceServiceProtocol[ResourceT]):
    """Provide the `create` and `save` methods for PyPaperless services."""

    _draft_cls: type[ResourceT]

    def create(self, **kwargs: Any) -> ResourceT:
        """Return a new draft :class:`~pypaperless.models.base.PaperlessModel` instance.

        The returned draft is not persisted until :meth:`save` is called.

        Example::

            draft = paperless.tags.create(name="urgent")
            draft.color = "#ff0000"
            new_id = await paperless.tags.save(draft)

        """
        if not hasattr(self, "_draft_cls"):
            message = "Service class has no _draft_cls attribute."
            raise DraftNotSupportedError(message)
        kwargs.update({"id": -1})

        return self._draft_cls.from_data(self._client, data=kwargs)

    async def save(self, draft: _DraftLike) -> int | str:
        """Persist a draft to Paperless and return the new resource identifier.

        Returns the created item ``id`` (``int``) for synchronous creation, or a
        Celery task UUID (``str``) for asynchronous creation (e.g. documents).

        Args:
            draft: A draft model instance created by :meth:`create`.

        Example::

            draft = paperless.documents.create(
                document=open("invoice.pdf", "rb").read(),
                title="Invoice",
            )
            task_id = await paperless.documents.save(draft)

        """
        draft.validate_draft()
        kwdict = draft.serialize()
        res = await self._client.transport.post(draft.api_path, **kwdict)

        if isinstance(res, dict):
            return int(res["id"])
        return str(res)
