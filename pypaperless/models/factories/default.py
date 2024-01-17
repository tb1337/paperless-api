"""Provide default factory classes."""

from typing import final

from pypaperless.const import API_PATH
from pypaperless.models import Document

from .base import FactoryBase


@final
class DocumentFactory(FactoryBase[type[Document]]):  # type: ignore[type-var]
    """Represent a factory for Paperless `Document` models."""

    _api_path = API_PATH["documents"]
    _resource = Document
