"""Provide default factory classes."""

from pypaperless.const import API_PATH
from pypaperless.models import Document

from .base import FactoryBase


class DocumentFactory(FactoryBase[Document]):
    """DocumentFactory instantiates the FactoryBase class."""

    _resource = type[Document]

    api_path = API_PATH["documents"]
