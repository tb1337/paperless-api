"""SaveableMixin for PyPaperless models."""

from typing import TYPE_CHECKING, ClassVar, cast

if TYPE_CHECKING:
    from pypaperless import Paperless
    from pypaperless.const import PaperlessResource


class SaveableMixin:
    """Model shortcut: delegate save() to the bound service.

    Requires ``_resource`` to be set as a ``ClassVar[PaperlessResource]`` on the
    model. Intended for Draft models that implement ``CreatableMixin``.
    """

    _resource: ClassVar["PaperlessResource"]
    _client: "Paperless"

    async def save(self) -> int | str:
        """Persist this draft to Paperless and return the new resource id.

        Delegates to ``service.save()``.

        Example:
        -------
        ```python
        draft = paperless.tags.create(name="urgent")
        new_id = await draft.save()
        ```

        """
        return cast("int | str", await getattr(self._client, self._resource).save(self))
