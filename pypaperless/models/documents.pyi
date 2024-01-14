from pypaperless import Paperless as Paperless

from .base import PaperlessBase as PaperlessBase

class Document(PaperlessBase):
    id: int = ...
    title: str = ...
