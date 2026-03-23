"""DeletableModel for PyPaperless models."""

from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from pypaperless.const import PaperlessResource
    from pypaperless.runtime import PaperlessRuntime


class DeletableModel:
    """Model shortcut: delegate delete() to the bound service.

    Requires ``_resource`` to be set as a ``ClassVar[PaperlessResource]`` on the
    model. Its string value is the attribute name of the matching service on the
    ``PaperlessClient`` (e.g. ``_resource = PaperlessResource.DOCUMENTS``).
    """

    _resource: ClassVar["PaperlessResource"]
    _client: "PaperlessRuntime"

    async def delete(self, *, silent_fail: bool = False) -> None:
        """Delete this model instance from Paperless.  This action cannot be undone.

        Delegates to :meth:`~pypaperless.services.mixins.deletable.DeletableService.delete`.
        Raises :exc:`~pypaperless.exceptions.DeletionError` on failure unless
        *silent_fail* is ``True``.

        Args:
            silent_fail: When ``True``, swallow :exc:`~pypaperless.exceptions.DeletionError`
                         instead of raising it.

        Example::

            doc = await paperless.documents(42)
            await doc.delete()

            # silently ignore a failed deletion
            await doc.delete(silent_fail=True)

        """
        await getattr(self._client, self._resource).delete(self, silent_fail=silent_fail)
