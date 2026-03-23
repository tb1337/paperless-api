"""Provide `DocumentBulkEdit` service."""

from pypaperless.const import API_PATH
from pypaperless.exceptions import BulkEditError
from pypaperless.models.bulk_edit import CustomFieldsInput, EditPdfOperation, SourceMode
from pypaperless.models.mixins.securable import Permissions
from pypaperless.services.base import PaperlessService


class DocumentBulkEditService(PaperlessService):
    """Perform bulk operations on a list of documents."""

    _api_path = API_PATH["documents_bulk_edit"]

    async def _post(self, path: str, *, json: dict) -> None:
        """POST to *path* and raise `BulkEditError` when the result is not ``"OK"``."""
        data = await self._runtime.transport.post(path, json=json)
        if data.get("result") != "OK":
            raise BulkEditError(str(data.get("result")))

    async def set_correspondent(
        self,
        documents: list[int],
        correspondent: int | None,
    ) -> None:
        """Assign a correspondent to a list of documents in bulk.

        Args:
            documents:     List of document primary keys.
            correspondent: Correspondent primary key to assign, or ``None`` to clear.

        Example::

            await paperless.documents.bulk_edit.set_correspondent([1, 2, 3], 5)
            await paperless.documents.bulk_edit.set_correspondent([1, 2, 3], None)  # clear

        """
        payload = {
            "documents": documents,
            "method": "set_correspondent",
            "parameters": {"correspondent": correspondent},
        }
        await self._post(self._api_path, json=payload)

    async def set_document_type(
        self,
        documents: list[int],
        document_type: int | None,
    ) -> None:
        """Assign a document type to a list of documents in bulk.

        Args:
            documents:     List of document primary keys.
            document_type: DocumentType primary key to assign, or ``None`` to clear.

        Example::

            await paperless.documents.bulk_edit.set_document_type([1, 2], 3)
            await paperless.documents.bulk_edit.set_document_type([1, 2], None)  # clear

        """
        payload = {
            "documents": documents,
            "method": "set_document_type",
            "parameters": {"document_type": document_type},
        }
        await self._post(self._api_path, json=payload)

    async def set_storage_path(
        self,
        documents: list[int],
        storage_path: int | None,
    ) -> None:
        """Assign a storage path to a list of documents in bulk.

        Args:
            documents:    List of document primary keys.
            storage_path: StoragePath primary key to assign, or ``None`` to clear.

        Example::

            await paperless.documents.bulk_edit.set_storage_path([1, 2], 4)
            await paperless.documents.bulk_edit.set_storage_path([1, 2], None)  # clear

        """
        payload = {
            "documents": documents,
            "method": "set_storage_path",
            "parameters": {"storage_path": storage_path},
        }
        await self._post(self._api_path, json=payload)

    async def add_tag(
        self,
        documents: list[int],
        tag: int,
    ) -> None:
        """Add a tag to a list of documents in bulk.

        Args:
            documents: List of document primary keys.
            tag:       Tag primary key to add.

        Example::

            await paperless.documents.bulk_edit.add_tag([1, 2, 3], 7)

        """
        payload = {
            "documents": documents,
            "method": "add_tag",
            "parameters": {"tag": tag},
        }
        await self._post(self._api_path, json=payload)

    async def remove_tag(
        self,
        documents: list[int],
        tag: int,
    ) -> None:
        """Remove a tag from a list of documents in bulk.

        Args:
            documents: List of document primary keys.
            tag:       Tag primary key to remove.

        Example::

            await paperless.documents.bulk_edit.remove_tag([1, 2, 3], 7)

        """
        payload = {
            "documents": documents,
            "method": "remove_tag",
            "parameters": {"tag": tag},
        }
        await self._post(self._api_path, json=payload)

    async def modify_tags(
        self,
        documents: list[int],
        *,
        add_tags: list[int],
        remove_tags: list[int],
    ) -> None:
        """Add and/or remove tags on a list of documents in bulk.

        Args:
            documents:   List of document primary keys.
            add_tags:    List of tag primary keys to add.
            remove_tags: List of tag primary keys to remove.

        Example::

            await paperless.documents.bulk_edit.modify_tags(
                [1, 2, 3],
                add_tags=[5, 6],
                remove_tags=[2],
            )

        """
        payload = {
            "documents": documents,
            "method": "modify_tags",
            "parameters": {"add_tags": add_tags, "remove_tags": remove_tags},
        }
        await self._post(self._api_path, json=payload)

    async def modify_custom_fields(
        self,
        documents: list[int],
        *,
        add_custom_fields: CustomFieldsInput,
        remove_custom_fields: CustomFieldsInput,
    ) -> None:
        """Add and/or remove custom field values on a list of documents in bulk.

        Args:
            documents:            List of document primary keys.
            add_custom_fields:    Custom fields to add — either a list of PKs or
                                  a ``{pk: value}`` dict.
            remove_custom_fields: Custom fields to remove — either a list of PKs or
                                  a ``{pk: value}`` dict.

        Example::

            await paperless.documents.bulk_edit.modify_custom_fields(
                [1, 2],
                add_custom_fields={3: "open"},
                remove_custom_fields=[4],
            )

        """
        payload = {
            "documents": documents,
            "method": "modify_custom_fields",
            "parameters": {
                "add_custom_fields": add_custom_fields,
                "remove_custom_fields": remove_custom_fields,
            },
        }
        await self._post(self._api_path, json=payload)

    async def set_permissions(
        self,
        documents: list[int],
        *,
        owner: int | None = None,
        permissions: Permissions | None = None,
        merge: bool = False,
    ) -> None:
        """Set owner and/or permissions on a list of documents in bulk.

        Args:
            documents:   List of document primary keys.
            owner:       New owner user ID, or ``None`` to leave unchanged.
            permissions: A :class:`~pypaperless.models.mixins.securable.Permissions`
                         object describing view/change grants.  Pass ``None`` to
                         leave existing permissions unchanged.
            merge:       When ``True``, permissions are *merged* with existing ones
                         instead of replacing them.  Owner is only updated for
                         documents that currently have no owner.

        Example::

            from pypaperless.models.types import Permissions
            await paperless.documents.bulk_edit.set_permissions(
                [1, 2, 3],
                owner=1,
                permissions=Permissions(view_users=[2, 3], change_users=[1]),
            )

        """
        parameters: dict = {"merge": merge}
        if owner is not None:
            parameters["owner"] = owner
        if permissions is not None:
            parameters["set_permissions"] = permissions.model_dump()
        payload = {
            "documents": documents,
            "method": "set_permissions",
            "parameters": parameters,
        }
        await self._post(self._api_path, json=payload)

    async def delete(self, documents: list[int]) -> None:
        """Move a list of documents to the trash.

        Args:
            documents: List of document primary keys to move to trash.

        Example::

            await paperless.documents.bulk_edit.delete([10, 11, 12])

        """
        await self._post(API_PATH["documents_delete"], json={"documents": documents})

    async def reprocess(self, documents: list[int]) -> None:
        """Reprocess (re-run OCR) on a list of documents.

        Args:
            documents: List of document primary keys to reprocess.

        Example::

            await paperless.documents.bulk_edit.reprocess([1, 2, 3])

        """
        await self._post(API_PATH["documents_reprocess"], json={"documents": documents})

    async def rotate(
        self,
        documents: list[int],
        degrees: int,
        *,
        source_mode: SourceMode = "latest_version",
    ) -> None:
        """Rotate one or more documents by the given degrees.

        Args:
            documents:   List of document primary keys to rotate.
            degrees:     Rotation angle in degrees (e.g. ``90``, ``180``, ``270``).
            source_mode: Whether to operate on ``"latest_version"`` or ``"original"``.

        Example::

            await paperless.documents.bulk_edit.rotate([1, 2], 90)

        """
        payload = {
            "documents": documents,
            "degrees": degrees,
            "source_mode": source_mode,
        }
        await self._post(API_PATH["documents_rotate"], json=payload)

    async def merge(
        self,
        documents: list[int],
        *,
        metadata_document_id: int | None = None,
        delete_originals: bool = False,
        archive_fallback: bool = False,
        source_mode: SourceMode = "latest_version",
    ) -> None:
        """Merge multiple documents into a single new document.

        Args:
            documents:            List of document primary keys to merge.
            metadata_document_id: Primary key of the document whose metadata
                                  should be used for the merged result.  Pass
                                  ``None`` to use defaults.
            delete_originals:     When ``True``, source documents are moved to
                                  trash after merging.
            archive_fallback:     When ``True``, use the archived version when the
                                  original is unavailable.
            source_mode:          Whether to operate on ``"latest_version"`` or
                                  ``"original"``.

        Example::

            await paperless.documents.bulk_edit.merge(
                [10, 11, 12],
                metadata_document_id=10,
                delete_originals=True,
            )

        """
        payload: dict = {
            "documents": documents,
            "delete_originals": delete_originals,
            "archive_fallback": archive_fallback,
            "source_mode": source_mode,
        }
        if metadata_document_id is not None:
            payload["metadata_document_id"] = metadata_document_id
        await self._post(API_PATH["documents_merge"], json=payload)

    async def edit_pdf(
        self,
        document: int,
        operations: list[EditPdfOperation],
        *,
        delete_original: bool = False,
        update_document: bool = False,
        include_metadata: bool = True,
        source_mode: SourceMode = "latest_version",
    ) -> None:
        """Apply PDF page-level operations (rotate, reorder, remove) to a document.

        Note: the API only supports a **single** document per request.

        Args:
            document:         Primary key of the document to edit.
            operations:       List of page operations.  Each entry must have a
                              required ``"page"`` key and optional ``"rotate"``
                              and ``"doc"`` keys.
            delete_original:  When ``True``, the source document is moved to trash
                              after editing.
            update_document:  When ``True``, the source document is updated in-place
                              rather than creating a new document.
            include_metadata: When ``True``, metadata is carried over to the
                              resulting document.
            source_mode:      Whether to operate on ``"latest_version"`` or
                              ``"original"``.

        Example::

            await paperless.documents.bulk_edit.edit_pdf(
                42,
                operations=[{"page": 1, "rotate": 90}, {"page": 3}],
                delete_original=True,
            )

        """
        payload = {
            "documents": [document],
            "operations": list(operations),
            "delete_original": delete_original,
            "update_document": update_document,
            "include_metadata": include_metadata,
            "source_mode": source_mode,
        }
        await self._post(API_PATH["documents_edit_pdf"], json=payload)

    async def remove_password(
        self,
        documents: list[int],
        password: str,
        *,
        update_document: bool = False,
        delete_original: bool = False,
        include_metadata: bool = True,
        source_mode: SourceMode = "latest_version",
    ) -> None:
        """Remove password protection from one or more PDF documents.

        Args:
            documents:        List of document primary keys.
            password:         Current PDF password to unlock the file.
            update_document:  When ``True``, the source documents are updated in-place.
            delete_original:  When ``True``, the original documents are moved to
                              trash after decryption.
            include_metadata: When ``True``, metadata is carried over.
            source_mode:      Whether to operate on ``"latest_version"`` or
                              ``"original"``.

        Example::

            await paperless.documents.bulk_edit.remove_password(
                [5, 6],
                password="secret",
                delete_original=True,
            )

        """
        payload = {
            "documents": documents,
            "password": password,
            "update_document": update_document,
            "delete_original": delete_original,
            "include_metadata": include_metadata,
            "source_mode": source_mode,
        }
        await self._post(API_PATH["documents_remove_password"], json=payload)
