"""Provide `BulkEditObjects` service."""

from pypaperless.const import API_PATH
from pypaperless.models.bulk_edit import BulkEditObjectType
from pypaperless.models.mixins.securable import Permissions

from .base import PaperlessService


class BulkEditObjectsService(PaperlessService):
    """Perform bulk operations on non-document objects (tags, correspondents, etc.)."""

    _api_path = API_PATH["bulk_edit_objects"]

    async def set_permissions(
        self,
        object_type: BulkEditObjectType,
        objects: list[int],
        *,
        owner: int | None = None,
        permissions: Permissions | None = None,
        merge: bool = False,
    ) -> None:
        """Set owner and/or permissions on a list of objects in bulk.

        Args:
            object_type: Resource type — one of ``"tags"``, ``"correspondents"``,
                         ``"document_types"``, or ``"storage_paths"``.
            objects:     List of primary keys to operate on.
            owner:       New owner user ID.  Pass ``None`` to leave unchanged.
            permissions: A :class:`~pypaperless.models.mixins.securable.Permissions`
                         object describing view/change grants.  Pass ``None`` to
                         leave existing permissions unchanged.
            merge:       When ``True``, the provided permissions are *merged* with
                         the existing ones instead of replacing them.  Ownership
                         is only updated for objects that currently have no owner.

        Example::

            from pypaperless.models.types import Permissions
            await paperless.bulk_edit_objects.set_permissions(
                "tags",
                [1, 2, 3],
                owner=1,
                permissions=Permissions(view_users=[2], change_users=[1]),
            )

        """
        payload: dict = {
            "objects": objects,
            "object_type": object_type,
            "operation": "set_permissions",
            "merge": merge,
        }
        if owner is not None:
            payload["owner"] = owner
        if permissions is not None:
            payload["permissions"] = permissions.model_dump()
        await self._client.request_json("post", self._api_path, json=payload)

    async def delete(
        self,
        object_type: BulkEditObjectType,
        objects: list[int],
    ) -> None:
        """Permanently delete a list of objects.

        Args:
            object_type: Resource type — one of ``"tags"``, ``"correspondents"``,
                         ``"document_types"``, or ``"storage_paths"``.
            objects:     List of primary keys to delete.

        Example::

            await paperless.bulk_edit_objects.delete("correspondents", [4, 5])

        """
        payload = {
            "objects": objects,
            "object_type": object_type,
            "operation": "delete",
        }
        await self._client.request_json("post", self._api_path, json=payload)
