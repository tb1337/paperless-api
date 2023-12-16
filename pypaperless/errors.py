"""PyPaperless errors."""


class PaperlessException(Exception):
    """Base exception for paperless."""


class BadRequestException(PaperlessException):
    """Raised when requesting wrong data."""
