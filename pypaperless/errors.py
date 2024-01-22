"""PyPaperless errors."""


class PaperlessException(Exception):
    """Base exception for PyPaperless."""


class DraftNotSupported(PaperlessException):
    """Raise when trying to draft unsupported models."""


class DraftFieldRequired(PaperlessException):
    """Raise when trying to save models with missing required fields."""


class BadRequestException(PaperlessException):
    """Raise when requesting wrong data."""


class DataNotExpectedException(PaperlessException):
    """Raise when expecting a type and receiving something else."""


class ControllerConfusion(PaperlessException):
    """Raise when Paperless version does not match to controllers."""
