"""Setup pytest."""

import pytest

from pypaperless import Paperless

from . import PaperlessMock

PAPERLESS_TEST_URL = "local.test"
PAPERLESS_TEST_TOKEN = "abcdef123467980"
PAPERLESS_TEST_REQ_OPTS = {"ssl": False}


@pytest.fixture
def api() -> Paperless:
    """Return a mock Paperless."""
    return PaperlessMock(
        PAPERLESS_TEST_URL,
        PAPERLESS_TEST_TOKEN,
        request_opts=PAPERLESS_TEST_REQ_OPTS,
    )


@pytest.fixture
def api_v0_0_0(api) -> Paperless:
    """Return a basic Paperless object."""
    return api


@pytest.fixture
def api_v1_8_0(api) -> Paperless:
    """Return a Paperless object with given version."""
    api.version = "1.8.0"
    return api
