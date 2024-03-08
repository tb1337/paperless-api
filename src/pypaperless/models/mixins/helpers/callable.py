"""CallableMixin for PyPaperless helpers."""

from pypaperless.models.base import HelperProtocol, ResourceT

from .securable import SecurableMixin


class CallableMixin(HelperProtocol[ResourceT]):
    """Provide methods for calling a specific resource item."""

    async def __call__(
        self,
        pk: int,
        *,
        lazy: bool = False,
    ) -> ResourceT:
        """Request exactly one resource item.

        Example:
        -------
        ```python
        # request a document
        document = await paperless.documents(42)

        # initialize a model and request it later
        document = await paperless.documents(42, lazy=True)
        ```

        """
        data = {
            "id": pk,
        }
        item = self._resource_cls.create_with_data(self._api, data)

        # set requesting full permissions
        if SecurableMixin in type(self).__bases__ and getattr(self, "_request_full_perms", False):
            item._params.update({"full_perms": "true"})  # noqa: SLF001

        if not lazy:
            await item.load()
        return item
