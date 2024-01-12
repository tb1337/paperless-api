"""Controller for Paperless documents resource."""

from typing import TYPE_CHECKING

from pypaperless.const import PaperlessFeature
from pypaperless.models import (
    Document,
    DocumentMetaInformation,
    DocumentNote,
    DocumentNotePost,
    DocumentPost,
)
from pypaperless.models.custom_fields import CustomFieldValue
from pypaperless.util import dataclass_from_dict, dataclass_to_dict

from .base import (
    BaseController,
    BaseService,
    DeleteMixin,
    ListMixin,
    OneMixin,
    PaginationMixin,
    UpdateMixin,
)

if TYPE_CHECKING:
    from pypaperless import Paperless

_DocumentOrIdType = Document | int


def _get_document_id_helper(item: _DocumentOrIdType) -> int:
    """Return a document id from object or int."""
    if isinstance(item, Document):
        return item.id
    return int(item)


class DocumentCustomFieldsService(BaseService):  # pylint: disable=too-few-public-methods
    """Handle manipulation of custom field value instances."""

    async def __call__(
        self,
        obj: _DocumentOrIdType,
        cf: list[CustomFieldValue],
    ) -> Document:
        """Add or change custom field value."""
        idx = _get_document_id_helper(obj)
        url = f"{self._path}/{idx}/"
        payload = {
            "custom_fields": [dataclass_to_dict(item) for item in cf],
        }
        res = await self._paperless.request_json("patch", url, json=payload)
        data: Document = dataclass_from_dict(Document, res)
        return data


class DocumentNotesService(BaseService):
    """Handle http requests for document notes sub-endpoint."""

    async def get(self, obj: _DocumentOrIdType) -> list[DocumentNote]:
        """Request document notes of given document."""
        idx = _get_document_id_helper(obj)
        url = f"{self._path}/{idx}/notes"
        res = await self._paperless.request_json("get", url)

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
        """Create a new document note. Raise on failure."""
        url = f"{self._path}/{obj.document}/notes"
        await self._paperless.request_json("post", url, json=dataclass_to_dict(obj))

    async def delete(self, obj: DocumentNote) -> None:
        """Delete an existing document note. Raise on failure."""
        url = f"{self._path}/{obj.document}/notes"
        params = {
            "id": obj.id,
        }
        await self._paperless.request_json("delete", url, params=params)


class DocumentFilesService(BaseService):
    """Handle http requests for document files downloading."""

    async def _get_data(
        self,
        path: str,
        idx: int,
    ) -> bytes:
        """Request a child endpoint."""
        url = f"{self._path}/{idx}/{path}"
        return await self._paperless.request_file("get", url)

    async def download(self, obj: _DocumentOrIdType) -> bytes:
        """Request document endpoint for downloading the actual file."""
        return await self._get_data("download", _get_document_id_helper(obj))

    async def preview(self, obj: _DocumentOrIdType) -> bytes:
        """Request document endpoint for previewing the actual file."""
        return await self._get_data("preview", _get_document_id_helper(obj))

    async def thumb(self, obj: _DocumentOrIdType) -> bytes:
        """Request document endpoint for the thumbnail file."""
        return await self._get_data("thumb", _get_document_id_helper(obj))


class DocumentsController(  # pylint: disable=too-many-ancestors
    BaseController[Document],
    PaginationMixin[Document],
    ListMixin[Document],
    OneMixin[Document],
    UpdateMixin[Document],
    DeleteMixin[Document],
):
    """Represent Paperless documents resource."""

    _resource = Document
    _page_size = 100

    def __init__(self, paperless: "Paperless", path: str) -> None:
        """Override initialize controller. Also initialize service controllers."""
        super().__init__(paperless, path)

        self.files = DocumentFilesService(self)
        self.notes: DocumentNotesService | None = None
        self.custom_fields: DocumentCustomFieldsService | None = None

        if PaperlessFeature.FEATURE_DOCUMENT_NOTES in self._paperless.features:
            self.notes = DocumentNotesService(self)
        if PaperlessFeature.CONTROLLER_CUSTOM_FIELDS in self._paperless.features:
            self.custom_fields = DocumentCustomFieldsService(self)

    async def create(self, obj: DocumentPost) -> str:
        """Create a new document. Raise on failure."""
        url = f"{self.path}/post_document/"
        # result is a string in this case
        res: str = await self._paperless.request_json("post", url, form=dataclass_to_dict(obj))
        return res

    async def meta(self, obj: _DocumentOrIdType) -> DocumentMetaInformation:
        """Request document metadata of given document."""
        idx = _get_document_id_helper(obj)
        url = f"{self.path}/{idx}/metadata"
        res = await self._paperless.request_json("get", url)
        data: DocumentMetaInformation = dataclass_from_dict(DocumentMetaInformation, res)
        return data
