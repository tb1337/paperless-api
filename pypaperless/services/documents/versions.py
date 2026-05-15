"""Provide `DocumentVersionService` and `DocumentRootService`."""

from typing import IO

from pypaperless.const import EndpointPath, PaperlessResource
from pypaperless.models.documents.versions import DocumentRoot, DocumentVersionInfo

from .base import DocumentScopedServiceBase


class DocumentVersionService(DocumentScopedServiceBase):
    """Represent a service for managing versions of a Paperless `Document`."""

    _api_path = EndpointPath.DOCUMENTS_VERSION
    _resource = PaperlessResource.DOCUMENTS

    _resource_cls = DocumentVersionInfo

    async def upload(
        self,
        file: IO[bytes],
        *,
        version_label: str | None = None,
        pk: int | None = None,
    ) -> None:
        """Upload a new version of a document.

        Args:
            file:          Binary file-like object to upload as the new version.
            version_label: Optional human-readable label for this version.
            pk:            Document primary key.  May be omitted when the service is
                           accessed via a :class:`~pypaperless.models.documents.document.Document`
                           instance (``doc.versions.upload(file)``).

        Example::

            with open("updated.pdf", "rb") as f:
                await paperless.documents.versions.upload(f, version_label="v2", pk=42)

        """
        doc_pk = self._get_document_pk(pk)
        api_path = EndpointPath.DOCUMENTS_UPDATE_VERSION.format(pk=doc_pk)
        form: dict[str, object] = {"document": file}
        if version_label is not None:
            form["version_label"] = version_label
        res = await self._runtime.transport.request_raw("post", api_path, form=form)
        res.raise_for_status()

    async def update(
        self,
        version_id: int,
        *,
        version_label: str | None = None,
        pk: int | None = None,
    ) -> DocumentVersionInfo:
        """Update the label of a specific document version.

        Args:
            version_id:    ID of the version to update.
            version_label: New label to assign to the version.
            pk:            Document primary key.  May be omitted when the service is
                           accessed via a :class:`~pypaperless.models.documents.document.Document`
                           instance (``doc.versions.update(1, version_label="v2")``).

        Example::

            result = await paperless.documents.versions.update(
                1, version_label="v2", pk=42
            )
            print(result.version_label)

        """
        doc_pk = self._get_document_pk(pk)
        api_path = EndpointPath.DOCUMENTS_VERSION.format(pk=doc_pk, version_id=version_id)
        data = await self._runtime.transport.patch(api_path, json={"version_label": version_label})
        return self._resource_cls.from_data(self._runtime, data)

    async def delete(
        self,
        version_id: int,
        *,
        pk: int | None = None,
    ) -> None:
        """Delete a specific document version.

        Args:
            version_id: ID of the version to delete.
            pk:         Document primary key.  May be omitted when the service is
                        accessed via a :class:`~pypaperless.models.documents.document.Document`
                        instance (``doc.versions.delete(1)``).

        Example::

            await paperless.documents.versions.delete(1, pk=42)

        """
        doc_pk = self._get_document_pk(pk)
        api_path = EndpointPath.DOCUMENTS_VERSION.format(pk=doc_pk, version_id=version_id)
        await self._runtime.transport.delete(api_path)


class DocumentRootService(DocumentScopedServiceBase):
    """Represent a factory for Paperless `DocumentRoot` models."""

    _api_path = EndpointPath.DOCUMENTS_ROOT
    _resource = PaperlessResource.DOCUMENTS

    _resource_cls = DocumentRoot

    async def __call__(self, pk: int | None = None) -> DocumentRoot:
        """Return the root-document record for a document.

        Args:
            pk: Document primary key.  May be omitted when the service is
                accessed via a :class:`~pypaperless.models.documents.document.Document`
                instance (``doc.root()``).

        Example::

            result = await paperless.documents.root(42)
            print(result.root_id)

        """
        doc_pk = self._get_document_pk(pk)
        api_path = self._api_path.format(pk=doc_pk)
        data = await self._runtime.transport.get(api_path)
        return self._resource_cls.from_data(self._runtime, data)
