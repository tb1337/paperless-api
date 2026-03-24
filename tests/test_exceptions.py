"""Tests for exception classes: formatting."""

import re

import pytest

from pypaperless.exceptions import (
    JsonResponseWithError,
)


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
