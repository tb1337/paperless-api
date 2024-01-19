"""Provide default helper classes."""

from typing import final

from pypaperless.const import API_PATH
from pypaperless.models import Document

from .base import HelperBase
from .mixins import CallableMixin, IterableMixin


@final
class DocumentHelper(
    HelperBase[Document],
    CallableMixin[Document],
    IterableMixin[Document],
):
    """Represent a factory for Paperless `Document` models."""

    _api_path = API_PATH["documents"]
    _resource = Document
