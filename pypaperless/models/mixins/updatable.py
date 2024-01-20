"""UpdatableMixin for PyPaperless models."""

from typing import final

from pypaperless.models.base import PaperlessModelProtocol, ResourceT


class UpdatableMixin(PaperlessModelProtocol[ResourceT]):
    """Provide methods for calling a specific resource item."""

    @final
    async def update(self) -> bool:
        """Write `model data` to DRF. Actually changed attributes will get patched only.

        Example:
        ```python
        # request a document
        document = await paperless.documents(42)

        document.title = "New Title"

        # persist change
        if await document.update():
            # do something
        ```
        """
        # if not dataclasses.is_dataclass(self):
        #     raise ValueError("Class is no dataclass.")

        changed = {}
        # for field in dataclasses.fields(self):
        for name, value in self.__dict__.items():
            # value = object_to_dict_value(getattr(self, field.name))

            # if value != self._data[field.name]:  # type: ignore[union-attr]
            # changed[field.name] = value

            changed[name] = value

        if len(changed) == 0:
            return False

        self._data = await self._api.request_json("patch", self.api_path, json=changed)
        # self._set_dataclass_fields()

        return True
