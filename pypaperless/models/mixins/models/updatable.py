"""UpdatableMixin for PyPaperless models."""

from copy import deepcopy
from typing import Any

from pypaperless.models.base import PaperlessModelProtocol
from pypaperless.models.utils import object_to_dict_value

from .securable import SecurableMixin


class UpdatableMixin(PaperlessModelProtocol):
    """Provide the `update` method for PyPaperless models."""

    _data: dict[str, Any]

    async def update(self, *, only_changed: bool = True) -> bool:
        """Send actually changed `model data` to DRF.

        Return `True` when any attribute was updated, `False` otherwise.

        Example:
        -------
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

    def _check_permissions_field(self, data: dict) -> None:
        """Check."""
        if SecurableMixin not in type(self).__bases__:
            return
        if not self.has_permissions:  # type: ignore[attr-defined]
            return
        if "permissions" in data:
            data["set_permissions"] = deepcopy(data["permissions"])
            del data["permissions"]

    async def _patch_fields(self) -> bool:
        """Use the http `PATCH` method for updating only changed fields."""
        changed = {}
        for field in self._get_dataclass_fields():
            new_value = object_to_dict_value(getattr(self, field.name))

            if field.name in self._data and new_value != self._data[field.name]:
                changed[field.name] = new_value

        if len(changed) == 0:
            return False

        self._check_permissions_field(changed)

        self._data = await self._api.request_json(
            "patch",
            self._api_path,
            json=changed,
            params=self._params,
        )
        return True

    async def _put_fields(self) -> bool:
        """Use the http `PUT` method to replace all fields."""
        data = {
            field.name: object_to_dict_value(getattr(self, field.name))
            for field in self._get_dataclass_fields()
        }

        self._check_permissions_field(data)

        self._data = await self._api.request_json(
            "put",
            self._api_path,
            json=data,
            params=self._params,
        )
        return True
