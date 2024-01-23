"""UpdatableMixin for PyPaperless models."""

from typing import Any, final

from pypaperless.models.base import PaperlessModelProtocol
from pypaperless.util import object_to_dict_value


class UpdatableMixin(PaperlessModelProtocol):  # pylint: disable=too-few-public-methods
    """Provide the `update` method for PyPaperless models."""

    _data: dict[str, Any]

    @final
    async def update(self, only_changed: bool = True) -> bool:
        """Send actually changed `model data` to DRF.

        Return `True` when any attribute was updated, `False` otherwise.

        Example:
        ```python
        # request a document
        document = await paperless.documents(42)

        document.title = "New Title"
        if await document.update():
            print("Successfully updated a field!")
        ```
        """
        updated = False

        if only_changed:
            updated = await self._patch_fields()
        else:
            updated = await self._put_fields()

        self._set_dataclass_fields()
        return updated

    @final
    async def _patch_fields(self) -> bool:
        """Use the http `PATCH` method for updating only changed fields."""
        changed = {}
        for field in self._get_dataclass_fields():
            new_value = object_to_dict_value(getattr(self, field.name))

            if new_value != self._data[field.name]:
                changed[field.name] = new_value

        if len(changed) == 0:
            return False

        self._data = await self._api.request_json(
            "patch",
            self._api_path,
            json=changed,
        )
        return True

    @final
    async def _put_fields(self) -> bool:
        """Use the http `PUT` method to replace all fields."""
        data = {
            field.name: object_to_dict_value(getattr(self, field.name))
            for field in self._get_dataclass_fields()
        }
        self._data = await self._api.request_json("put", self._api_path, json=data)
        return True
