"""PyPaperless."""

from .paperless import Paperless
from .util import create_url_from_input

__all__ = (
    "Paperless",
    "create_url_from_input",
)
