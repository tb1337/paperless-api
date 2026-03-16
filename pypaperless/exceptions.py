"""PyPaperless exceptions."""

from typing import Any


class PaperlessError(Exception):
    """Base exception for PyPaperless."""


# Session / transport


class InitializationError(PaperlessError):
    """Raise when initializing a `Paperless` instance without valid url or token."""


class PaperlessConnectionError(InitializationError):
    """Raise when connection to Paperless is not possible."""


class AuthError(InitializationError):
    """Raise when response is 401 code."""


class InvalidTokenError(AuthError):
    """Raise when response is 401 due invalid access token."""


class InactiveOrDeletedError(AuthError):
    """Raise when response is 401 code due user is inactive or deleted."""


class ForbiddenError(InitializationError):
    """Raise when response is 403 code."""


# Response parsing


class ResponseError(PaperlessError):
    """Raise when the API returns an unexpected or error response."""


class BadJsonResponseError(ResponseError):
    """Raise when response is no valid json."""


class JsonResponseWithError(ResponseError):
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


# Draft lifecycle


class DraftError(PaperlessError):
    """Raise when a draft lifecycle operation fails."""


class DraftFieldRequiredError(DraftError):
    """Raise when trying to save models with missing required fields."""


class DraftNotSupportedError(DraftError):
    """Raise when trying to draft unsupported models."""


# Resource access


class ResourceError(PaperlessError):
    """Raise when a resource access or lookup operation fails."""


class ItemNotFoundError(ResourceError):
    """Raise when trying to access non-existing items in PaperlessModelData classes."""


class PrimaryKeyRequiredError(ResourceError):
    """Raise when trying to access model data without supplying a pk."""


class TaskNotFoundError(ResourceError):
    """Raise when trying to access a task by non-existing uuid."""

    def __init__(self, task_id: str) -> None:
        """Initialize a `TaskNotFound` instance."""
        super().__init__(f"Task with UUID {task_id} not found.")


# Document operations


class DocumentError(PaperlessError):
    """Raise when a document-specific service operation fails."""


class AsnRequestError(DocumentError):
    """Raise when getting an error during requesting the next asn."""


class SendEmailError(DocumentError):
    """Raise when sending email for a document fails."""
