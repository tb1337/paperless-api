"""UpdatableMixin for PyPaperless models."""

from typing import TYPE_CHECKING, ClassVar, cast

if TYPE_CHECKING:
    from pypaperless import Paperless
    from pypaperless.const import PaperlessResource


class UpdatableMixin:
    """Model shortcut: delegate update() to the bound service.

    Requires ``_resource`` to be set as a ``ClassVar[PaperlessResource]`` on the
    model. Its string value is the attribute name of the matching service on the
    ``Paperless`` client (e.g. ``_resource = PaperlessResource.DOCUMENTS``).
    """

    _resource: ClassVar["PaperlessResource"]
    _client: "Paperless"

    async def update(self, *, only_changed: bool = True) -> bool:
        """Persist changes on this model to Paperless.

        Delegates to ``service.update()``.

        Example:
        -------
        ```python
        doc = await paperless.documents(42)
        doc.title = "New Title"
        await doc.update()
        ```

        """
        return cast(
            "bool",
            await getattr(self._client, self._resource).update(self, only_changed=only_changed),
        )
