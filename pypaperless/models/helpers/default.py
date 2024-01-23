"""Provide default helper classes."""

from typing import TYPE_CHECKING, final

from pypaperless.const import API_PATH
from pypaperless.models import Document, DocumentDraft, DocumentMeta

from .base import HelperBase
from .mixins import CallableMixin, DraftableMixin, IterableMixin

if TYPE_CHECKING:
    from pypaperless import Paperless


@final
class DocumentMetaHelper(  # pylint: disable=too-few-public-methods
    HelperBase[DocumentMeta],
    CallableMixin[DocumentMeta],
):
    """Represent a factory for Paperless `DocumentMeta` models."""

    _api_path = API_PATH["documents_meta"]

    _resource = DocumentMeta


@final
class DocumentHelper(  # pylint: disable=too-many-ancestors
    HelperBase[Document],
    CallableMixin[Document],
    DraftableMixin[DocumentDraft],
    IterableMixin[Document],
):
    """Represent a factory for Paperless `Document` models."""

    _api_path = API_PATH["documents"]

    _draft = DocumentDraft
    _resource = Document

    def __init__(self, api: "Paperless") -> None:
        """Initialize a `DocumentHelper` instance."""
        super().__init__(api)

        self._meta = DocumentMetaHelper(api)

    @property
    def metadata(self) -> DocumentMetaHelper:
        """Return the attached `DocumentMetaHelper` instance.

        Example:
        ```python
        # request metadata of a document directly...
        metadata = await paperless.documents.metadata(1337)

        # ... or by using an already fetched document
        doc = await paperless.documents(42)
        metadata = await doc.get_metadata()
        ```
        """
        return self._meta
