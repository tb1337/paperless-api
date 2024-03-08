"""PyPaperless exceptions."""

from typing import Any


class PaperlessError(Exception):
    """Base exception for PyPaperless."""


# Sessions and requests


class AuthentificationRequiredError(PaperlessError):
    """Raise when initializing a `Paperless` instance without url/token or session."""


class RequestError(PaperlessError):
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
