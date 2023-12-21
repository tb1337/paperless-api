"""PyPaperless errors."""


class PaperlessException(Exception):
    """Base exception for PyPaperless."""


class BadRequestException(PaperlessException):
    """Raise when requesting wrong data."""


class DataNotExpectedException(PaperlessException):
    """Raise when expecting a type and receiving something else."""
