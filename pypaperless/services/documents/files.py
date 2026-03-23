"""Provide `Document` file retrieval services."""

from typing import Any, ClassVar

from pypaperless.const import API_PATH, PaperlessResource
from pypaperless.models.documents.document import DownloadedDocument, FileRetrieveMode
from pypaperless.services.base import ResourceService


class _DocumentFileServiceBase(ResourceService):
    """Base class for document file retrieval services (download, preview, thumbnail)."""

    _api_path = API_PATH["documents_download"]
    _resource = PaperlessResource.DOCUMENTS
    _mode: ClassVar[FileRetrieveMode]

    _resource_cls = DownloadedDocument

    async def __call__(self, pk: int, *, original: bool = False) -> DownloadedDocument:
        """Request exactly one resource item."""
        params = {
            "original": "true" if original else "false",
        }

        res = await self._client.transport.request(
            "get", self._api_path.format(pk=pk), params=params
        )

        data: dict[str, Any] = {
            "id": pk,
            "mode": self._mode,
            "original": original,
            "content": res.content,
            "content_type": res.headers.get("content-type"),
        }

        content_disposition = res.headers.get("content-disposition")
        if content_disposition is not None:
            parts = content_disposition.split(";")
            data["disposition_type"] = parts[0].strip()
            for part in parts[1:]:
                stripped = part.strip()
                if stripped.startswith("filename="):
                    data["disposition_filename"] = stripped.split("=", 1)[1].strip('"')

        return self._resource_cls.from_data(self._client, data)


class DocumentFileDownloadService(_DocumentFileServiceBase):
    """Retrieve the archived file of a document for download."""

    _api_path = API_PATH["documents_download"]
    _mode = FileRetrieveMode.DOWNLOAD


class DocumentFilePreviewService(_DocumentFileServiceBase):
    """Retrieve the archived file of a document for inline preview."""

    _api_path = API_PATH["documents_preview"]
    _mode = FileRetrieveMode.PREVIEW


class DocumentFileThumbnailService(_DocumentFileServiceBase):
    """Retrieve the thumbnail image of a document."""

    _api_path = API_PATH["documents_thumbnail"]
    _mode = FileRetrieveMode.THUMBNAIL
