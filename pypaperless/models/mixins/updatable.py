"""UpdatableMixin for PyPaperless models."""

from dataclasses import fields
from typing import Any, final

from pypaperless.models.base import PaperlessModelProtocol
from pypaperless.util import object_to_dict_value


class UpdatableMixin(PaperlessModelProtocol):
    """Provide methods for calling a specific resource item."""

    @final
    async def update(self) -> bool:
        """Send actually changed `model data` to DRF.

        Return `True` when any attribute was updated.

        Example:
        ```python
        # request a document
        document = await paperless.documents(42)

        document.title = "New Title"
        if await document.update():
            print("Successfully updated a field!")
        ```
        """

        changed = {}
        for field in self._get_dataclass_fields():
            new_value = object_to_dict_value(getattr(self, field.name))

            if new_value != self._data[field.name]:
                changed[field.name] = new_value

        if len(changed) == 0:
            return False

        self._data: dict[str, Any] = await self._api.request_json(
            "patch", self._api_path, json=changed
        )
        self._set_dataclass_fields()

        return True
