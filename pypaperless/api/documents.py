"""Customized endpoint for Paperless documents."""

from typing import TYPE_CHECKING

from aiohttp import FormData

from pypaperless.models import (
    Document,
    DocumentMetaInformation,
    DocumentNote,
    DocumentNotePost,
    DocumentPost,
)
from pypaperless.models.shared import ResourceType
from pypaperless.util import dataclass_from_dict, dataclass_to_dict

from .base import RT, BaseEndpoint, BaseEndpointCrudMixin, BaseService

if TYPE_CHECKING:
    from pypaperless import Paperless

DocumentOrIdType = Document | int


def _get_document_id_helper(item: DocumentOrIdType) -> int:
    """Return a document id from object or int."""
    if isinstance(item, Document):
        return item.id
    return int(item)


class DocumentNotesService(BaseService):
    """Handle http requests for document notes sub-endpoint."""

    async def get(self, obj: DocumentOrIdType) -> list[DocumentNote]:
        """Request document notes of given document."""
        idx = _get_document_id_helper(obj)
        url = f"{self.endpoint}/{idx}/notes"
        res = await self._paperless.request("get", url)

        # We have to transform data here slightly.
        # There are two major differences in the data depending on which endpoint is requested.
        # url: documents/{:pk}/ ->
        #       .document -> int
        #       .user -> int
        # url: documents/{:pk}/notes/ ->
        #       .document -> does not exist (so we add it here)
        #       .user -> dict(id=int, username=str, first_name=str, last_name=str)
        return [
            dataclass_from_dict(DocumentNote, {**item, "document": idx, "user": item["user"]["id"]})
            for item in res
        ]

    async def create(self, obj: DocumentNotePost) -> None:
        """Create a new document note. Raises on failure."""
        url = f"{self.endpoint}/{obj.document}/notes"
        await self._paperless.request("post", url, json=dataclass_to_dict(obj))

    async def delete(self, obj: DocumentNote) -> None:
        """Delete an existing document note. Raises on failure."""
        url = f"{self.endpoint}/{obj.document}/notes"
        params = {
            "id": obj.id,
        }
        await self._paperless.request("delete", url, params=params)


class DocumentFilesService(BaseService):
    """Handle http requests for document files downloading."""

    async def _get_data(
        self,
        path: str,
        idx: int,
    ) -> bytes:
        """Request a child endpoint."""
        url = f"{self.endpoint}/{idx}/{path}"
        return await self._paperless.request("get", url)

    async def download(self, obj: DocumentOrIdType) -> bytes:
        """Request document endpoint for downloading the actual file."""
        return await self._get_data("download", _get_document_id_helper(obj))

    async def preview(self, obj: DocumentOrIdType) -> bytes:
        """Request document endpoint for previewing the actual file."""
        return await self._get_data("preview", _get_document_id_helper(obj))

    async def thumb(self, obj: DocumentOrIdType) -> bytes:
        """Request document endpoint for the thumbnail file."""
        return await self._get_data("thumb", _get_document_id_helper(obj))


class DocumentsEndpoint(BaseEndpoint[type[Document]], BaseEndpointCrudMixin):
    """Represent Paperless document resource endpoint."""

    endpoint_cls = Document
    endpoint_type = ResourceType.DOCUMENTS

    request_page_size = 100

    def __init__(self, paperless: "Paperless", endpoint: ResourceType) -> None:
        """Initialize sub endpoint services."""
        super().__init__(paperless, endpoint)

        self.notes = DocumentNotesService(self)
        self.files = DocumentFilesService(self)

    async def create(self, obj: DocumentPost) -> str:
        """Create a new document. Raise on failure."""
        form = FormData()

        form.add_field("document", obj.document)

        for field in (
            "title",
            "created",
            "correspondent",
            "document_type",
            "archive_serial_number",
        ):
            if obj[field]:
                form.add_field(field, obj[field])

        if obj.tags and isinstance(obj.tags, list):
            for tag in obj.tags:
                form.add_field("tags", f"{tag}")

        url = f"{self.endpoint}/post_document/"
        res = await self._paperless.request("post", url, data=form)
        return str(res)

    async def meta(self, obj: DocumentOrIdType) -> RT:
        """Request document metadata of given document."""
        idx = _get_document_id_helper(obj)
        url = f"{self.endpoint}/{idx}/metadata"
        res = await self._paperless.request("get", url)
        return dataclass_from_dict(DocumentMetaInformation, res)
