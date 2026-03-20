"""DeletableModel for PyPaperless models."""

from typing import TYPE_CHECKING, ClassVar, cast

if TYPE_CHECKING:
    from pypaperless import Paperless
    from pypaperless.const import PaperlessResource


class DeletableModel:
    """Model shortcut: delegate delete() to the bound service.

    Requires ``_resource`` to be set as a ``ClassVar[PaperlessResource]`` on the
    model. Its string value is the attribute name of the matching service on the
    ``Paperless`` client (e.g. ``_resource = PaperlessResource.DOCUMENTS``).
    """

    _resource: ClassVar["PaperlessResource"]
    _client: "Paperless"

    async def delete(self) -> bool:
        """Delete this model instance from Paperless.  This action cannot be undone.

        Delegates to :meth:`~pypaperless.services.mixins.deletable.DeletableService.delete`.

        Example::

            doc = await paperless.documents(42)
            await doc.delete()

        """
        return cast("bool", await getattr(self._client, self._resource).delete(self))
