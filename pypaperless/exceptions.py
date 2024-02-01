"""PyPaperless exceptions."""

from typing import Any


class PaperlessException(Exception):
    """Base exception for PyPaperless."""


# Sessions and requests


class RequestException(PaperlessException):
    """Raise when issuing a request fails."""

    def __init__(
        self,
        exc: Exception,
        req_args: tuple[str, str, dict[str, str | int] | None],
        req_kwargs: dict[str, Any] | None,
    ) -> None:
        """Initialize a `RequestException` instance."""
        message = f"Request error: {type(exc).__name__}\n"
        message += f"URL: {req_args[1]}\n"
        message += f"Method: {req_args[0].upper()}\n"
        message += f"params={req_args[2]}\n"
        message += f"kwargs={req_kwargs}"

        super().__init__(message)


class BadJsonResponse(PaperlessException):
    """Raise when response is no valid json."""


class JsonResponseWithError(PaperlessException):
    """Raise when Paperless accepted the request, but responded with an error payload."""

    def __init__(self, payload: Any) -> None:
        """Initialize a `JsonResponseWithError` instance."""
        message: Any = "Unknown error"

        if isinstance(payload, dict) and "error" in payload:
            message = payload["error"]
            if isinstance(message, list):
                message = "\n".join(message)

        super().__init__(f"Paperless: {message}")


# Models


class AsnRequestError(PaperlessException):
    """Raise when getting an error during requesting the next asn."""


class DraftFieldRequired(PaperlessException):
    """Raise when trying to save models with missing required fields."""


class DraftNotSupported(PaperlessException):
    """Raise when trying to draft unsupported models."""


class PrimaryKeyRequired(PaperlessException):
    """Raise when trying to access model data without supplying a pk."""


# Tasks


class TaskNotFound(PaperlessException):
    """Raise when trying to access a task by non-existing uuid."""

    def __init__(self, task_id: str) -> None:
        """Initialize a `TaskNotFound` instance."""
        super().__init__(f"Task with UUID {task_id} not found.")
