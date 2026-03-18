"""UpdatableMixin for PyPaperless services."""

from copy import deepcopy
from typing import Any

from pypaperless.models.base import ResourceT
from pypaperless.services.base import ResourceServiceProtocol
from pypaperless.utils import object_to_dict_value


class UpdatableMixin(ResourceServiceProtocol[ResourceT]):
    """Provide the `update` method for PyPaperless services."""

    async def update(self, model: ResourceT, *, only_changed: bool = True) -> bool:
        """Send actually changed `model data` to DRF.

        Return `True` when any attribute was updated, `False` otherwise.

        Example:
        -------
        ```python
        document = await paperless.documents(42)

        document.title = "New Title"
        if await paperless.documents.update(document):
            print("Successfully updated a field!")
        ```

        """
        params = self._get_request_params()

        if only_changed:
            updated = await self._patch_fields(model, params)
        else:
            updated = await self._put_fields(model, params)

        model.apply_data()
        return updated

    def _get_request_params(self) -> dict[str, Any]:
        """Build request parameters."""
        params: dict[str, Any] = {}
        if getattr(self, "_request_full_perms", False):
            params["full_perms"] = "true"
        return params

    @staticmethod
    def _check_permissions_field(model: ResourceT, data: dict) -> None:
        """Rewrite permissions field to set_permissions for DRF."""
        if not hasattr(model, "has_permissions"):
            return
        if not model.has_permissions:
            return
        if "permissions" in data:
            data["set_permissions"] = deepcopy(data["permissions"])
            del data["permissions"]

    async def _patch_fields(self, model: ResourceT, params: dict[str, Any]) -> bool:
        """Use the http `PATCH` method for updating only changed fields."""
        changed: dict[str, Any] = {}
        for name in model.__class__.model_fields:
            new_value = object_to_dict_value(getattr(model, name))

            if name in model.data and new_value != model.data[name]:
                changed[name] = new_value

        if len(changed) == 0:
            return False

        self._check_permissions_field(model, changed)

        model.data = await self._client.request_json(
            "patch",
            model.api_path,
            json=changed,
            params=params or None,
        )
        return True

    async def _put_fields(self, model: ResourceT, params: dict[str, Any]) -> bool:
        """Use the http `PUT` method to replace all fields."""
        data = {
            name: object_to_dict_value(getattr(model, name))
            for name in model.__class__.model_fields
        }

        self._check_permissions_field(model, data)

        model.data = await self._client.request_json(
            "put",
            model.api_path,
            json=data,
            params=params or None,
        )
        return True
