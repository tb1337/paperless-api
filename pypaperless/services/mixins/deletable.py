"""DeletableService for PyPaperless services."""

from pypaperless.models.base import ResourceT
from pypaperless.services.base import ResourceServiceProtocol


class DeletableService(ResourceServiceProtocol[ResourceT]):
    """Provide the `delete` method for PyPaperless services."""

    async def delete(self, model: ResourceT) -> bool:
        """Delete a resource item from Paperless.  This action cannot be undone.

        Returns ``True`` when the deletion was successful, ``False`` otherwise.

        Args:
            model: The model instance to delete.

        Example::

            document = await paperless.documents(42)
            if await paperless.documents.delete(document):
                print("Document deleted.")

        """
        res = await self._client.request("delete", model.api_path)
        return res.status_code == 204
