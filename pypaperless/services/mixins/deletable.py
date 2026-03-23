"""DeletableService for PyPaperless services."""

from pypaperless.exceptions import DeletionError
from pypaperless.models.base import ResourceT
from pypaperless.services.base import ResourceServiceProtocol


class DeletableService(ResourceServiceProtocol[ResourceT]):
    """Provide the `delete` method for PyPaperless services."""

    async def delete(self, model: ResourceT, *, silent_fail: bool = False) -> None:
        """Delete a resource item from Paperless.  This action cannot be undone.

        Raises :exc:`~pypaperless.exceptions.DeletionError` on failure unless
        *silent_fail* is ``True``.

        Args:
            model:       The model instance to delete.
            silent_fail: When ``True``, swallow :exc:`~pypaperless.exceptions.DeletionError`
                         instead of raising it.  All other exceptions still propagate.

        Example::

            document = await paperless.documents(42)
            # raises DeletionError on failure
            await paperless.documents.delete(document)

            # silently ignore a failed deletion
            await paperless.documents.delete(document, silent_fail=True)

        """
        try:
            await self._client.transport.delete(model.api_path)
        except DeletionError:
            if not silent_fail:
                raise
