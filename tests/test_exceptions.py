"""Tests for exception classes: hierarchy, backwards compatibility, formatting."""

import re

import pytest

from pypaperless.exceptions import (
    ForbiddenError,
    InactiveOrDeletedError,
    InitializationError,
    InvalidTokenError,
    JsonResponseWithError,
    PaperlessConnectionError,
)

# mypy: ignore-errors


@pytest.mark.parametrize(
    "exception_cls",
    [
        PaperlessConnectionError,
        InvalidTokenError,
        InactiveOrDeletedError,
        ForbiddenError,
    ],
)
def test_init_errors_are_backwards_compatible(exception_cls: type) -> None:
    """All initialization errors must be catchable as InitializationError."""
    assert issubclass(exception_cls, InitializationError)


@pytest.mark.parametrize(
    ("payload", "expected_message"),
    [
        (
            "sample string",
            "Paperless [error]: sample string",
        ),
        (
            {"failure": "something failed"},
            "Paperless [failure]: something failed",
        ),
        (
            {"error": ["that", "should", "have", "been", "never", "happened"]},
            "Paperless [error]: that",
        ),
        (
            [{"some": [[{"weird": {"error": ["occurred"]}}]]}],
            "Paperless [some -> weird -> error]: occurred",
        ),
    ],
)
def test_json_response_with_error_formatting(payload: object, expected_message: str) -> None:
    """JsonResponseWithError must format its message correctly for every payload shape."""
    with pytest.raises(JsonResponseWithError, match=re.escape(expected_message)):
        raise JsonResponseWithError(payload)
