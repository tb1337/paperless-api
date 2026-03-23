"""SaveableModel for PyPaperless models."""

from typing import TYPE_CHECKING, ClassVar, cast

if TYPE_CHECKING:
    from pypaperless.const import PaperlessResource
    from pypaperless.runtime import PaperlessRuntime


class SaveableModel:
    """Model shortcut: delegate save() to the bound service.

    Requires ``_resource`` to be set as a ``ClassVar[PaperlessResource]`` on the
    model. Intended for Draft models that implement ``CreatableModel``.
    """

    _resource: ClassVar["PaperlessResource"]
    _client: "PaperlessRuntime"

    async def save(self) -> int | str:
        """Persist this draft to Paperless and return the new resource identifier.

        Delegates to :meth:`~pypaperless.services.mixins.creatable.CreatableService.save`.

        Example::

            draft = paperless.tags.create(name="urgent")
            new_id = await draft.save()

        """
        return cast("int | str", await getattr(self._client, self._resource).save(self))
