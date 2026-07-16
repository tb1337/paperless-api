"""UpdatableService for PyPaperless services."""

from copy import deepcopy
from typing import Any, cast

from pypaperless.models.base import ResourceT
from pypaperless.services.base import ResourceServiceProtocol
from pypaperless.utils import object_to_dict_value


class UpdatableService(ResourceServiceProtocol[ResourceT]):
    """Provide the `update` method for PyPaperless services."""

    async def update(self, model: ResourceT, *, only_changed: bool = True) -> bool:
        """Send changed model data to Paperless.

        Returns ``True`` when at least one attribute was updated, ``False`` when
        nothing changed.

        Args:
            model:        The model instance with modified attributes.
            only_changed: When ``True`` (default), only changed fields are sent
                          via ``PATCH``.  Set to ``False`` to replace the full
                          resource via ``PUT``.

        Example::

            document = await paperless.documents(42)
            document.title = "New Title"
            if await paperless.documents.update(document):
                print("Updated.")

        """
        params = self._get_request_params()

        if only_changed:
            response = await self._patch_fields(model, params)
        else:
            response = await self._put_fields(model, params)

        if response is not None:
            model.refresh_from(response)
            return True
        return False

    def _get_request_params(self) -> dict[str, Any]:
        """Build request parameters."""
        params: dict[str, Any] = {}
        if getattr(self, "request_permissions", False):
            params["full_perms"] = "true"
        return params

    @staticmethod
    def _check_permissions_field(model: ResourceT, data: dict) -> None:
        """Rewrite the permissions field to set_permissions before sending to Paperless."""
        if not hasattr(model, "has_permissions"):
            return
        if not model.has_permissions:
            return
        if "permissions" in data:
            data["set_permissions"] = deepcopy(data["permissions"])
            del data["permissions"]

    async def _patch_fields(
        self, model: ResourceT, params: dict[str, Any]
    ) -> dict[str, Any] | None:
        """Use the http `PATCH` method for updating only changed fields."""
        changed: dict[str, Any] = {}
        for name in model.__class__.model_fields:
            new_value = object_to_dict_value(getattr(model, name))

            if name in model.snapshot and new_value != model.snapshot[name]:
                changed[name] = new_value

        if not changed:
            return None

        self._check_permissions_field(model, changed)

        return cast(
            "dict[str, Any]",
            await self._runtime.transport.patch(
                model.api_path,
                json=changed,
                params=params or None,
            ),
        )

    async def _put_fields(self, model: ResourceT, params: dict[str, Any]) -> dict[str, Any]:
        """Use the http `PUT` method to replace all fields."""
        data = {
            name: object_to_dict_value(getattr(model, name))
            for name in model.__class__.model_fields
        }

        self._check_permissions_field(model, data)

        return cast(
            "dict[str, Any]",
            await self._runtime.transport.put(
                model.api_path,
                json=data,
                params=params or None,
            ),
        )
