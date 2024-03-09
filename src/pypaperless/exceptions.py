"""PyPaperless exceptions."""

from typing import Any


class PaperlessError(Exception):
    """Base exception for PyPaperless."""


# Sessions and requests


class InitializationError(PaperlessError):
    """Raise when initializing a `Paperless` instance without valid url or token."""


class BadJsonResponseError(PaperlessError):
    """Raise when response is no valid json."""


class JsonResponseWithError(PaperlessError):
    """Raise when Paperless accepted the request, but responded with an error payload."""

    def __init__(self, payload: Any) -> None:
        """Initialize a `JsonResponseWithError` instance."""
        key: str = "error"
        message: Any = "unknown error"

        if isinstance(payload, dict):
            key = "error" if "error" in payload else set(payload.keys()).pop()
            message = payload[key]
            if isinstance(message, list):
                message = message.pop()

        super().__init__(f"Paperless: {key} - {message}")


# Models


class AsnRequestError(PaperlessError):
    """Raise when getting an error during requesting the next asn."""


class DraftFieldRequiredError(PaperlessError):
    """Raise when trying to save models with missing required fields."""


class DraftNotSupportedError(PaperlessError):
    """Raise when trying to draft unsupported models."""


class PrimaryKeyRequiredError(PaperlessError):
    """Raise when trying to access model data without supplying a pk."""


# Tasks


class TaskNotFoundError(PaperlessError):
    """Raise when trying to access a task by non-existing uuid."""

    def __init__(self, task_id: str) -> None:
        """Initialize a `TaskNotFound` instance."""
        super().__init__(f"Task with UUID {task_id} not found.")
