"""PyPaperless exceptions."""

from typing import Any


class PaperlessError(Exception):
    """Base exception for PyPaperless."""


# Sessions and requests


class InitializationError(PaperlessError):
    """Raise when initializing a `Paperless` instance without valid url or token."""


class PaperlessConnectionError(InitializationError, PaperlessError):
    """Raise when connection to Paperless is not possible."""


class PaperlessAuthError(InitializationError, PaperlessError):
    """Raise when response is 401 code."""


class PaperlessInvalidTokenError(PaperlessAuthError):
    """Raise when response is 401 due invalid access token."""


class PaperlessInactiveOrDeletedError(PaperlessAuthError):
    """Raise when response is 401 code due user is inactive or deleted."""


class PaperlessForbiddenError(InitializationError, PaperlessError):
    """Raise when response is 403 code."""


class BadJsonResponseError(PaperlessError):
    """Raise when response is no valid json."""


class JsonResponseWithError(PaperlessError):
    """Raise when Paperless accepted the request, but responded with an error payload."""

    def __init__(self, payload: Any) -> None:
        """Initialize a `JsonResponseWithError` instance."""

        def _parse_payload(payload: Any, key: list[str] | None = None) -> tuple[list[str], str]:
            """Parse first suitable error from payload."""
            if key is None:
                key = []

            if isinstance(payload, list):
                return _parse_payload(payload.pop(0), key)
            if isinstance(payload, dict):
                if "error" in payload:
                    key.append("error")
                    return _parse_payload(payload["error"], key)

                new_key = next(iter(payload))
                key.append(new_key)

                return _parse_payload(payload[new_key], key)

            return key, payload

        key, message = _parse_payload(payload)

        if len(key) == 0:
            key.append("error")
        key_chain = " -> ".join(key)

        super().__init__(f"Paperless [{key_chain}]: {message}")


# Models


class AsnRequestError(PaperlessError):
    """Raise when getting an error during requesting the next asn."""


class DraftFieldRequiredError(PaperlessError):
    """Raise when trying to save models with missing required fields."""


class DraftNotSupportedError(PaperlessError):
    """Raise when trying to draft unsupported models."""


class ItemNotFoundError(PaperlessError):
    """Raise when trying to access non-existing items in PaperlessModelData classes."""


class PrimaryKeyRequiredError(PaperlessError):
    """Raise when trying to access model data without supplying a pk."""


# Tasks


class TaskNotFoundError(PaperlessError):
    """Raise when trying to access a task by non-existing uuid."""

    def __init__(self, task_id: str) -> None:
        """Initialize a `TaskNotFound` instance."""
        super().__init__(f"Task with UUID {task_id} not found.")
