"""Provide default helper classes."""

from typing import final

from pypaperless.const import API_PATH
from pypaperless.models import Document, DocumentDraft, DocumentMeta

from .base import HelperBase
from .mixins import CallableMixin, DraftableMixin, IterableMixin


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


@final
class DocumentMetaHelper(  # pylint: disable=too-few-public-methods
    HelperBase[DocumentMeta],
    CallableMixin[DocumentMeta],
):
    """Represent a factory for Paperless `DocumentMeta` models."""

    _api_path = API_PATH["documents_meta"]

    _resource = DocumentMeta
