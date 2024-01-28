"""Setup pytest."""

import pytest

from pypaperless import Paperless

from . import PaperlessSessionMock
from .const import PAPERLESS_TEST_REQ_ARGS, PAPERLESS_TEST_TOKEN, PAPERLESS_TEST_URL

# mypy: ignore-errors


@pytest.fixture
def api() -> Paperless:
    """Return a mock Paperless."""
    session = PaperlessSessionMock(
        PAPERLESS_TEST_URL,
        PAPERLESS_TEST_TOKEN,
        **PAPERLESS_TEST_REQ_ARGS,
    )
    return Paperless(
        url=PAPERLESS_TEST_URL,
        token=PAPERLESS_TEST_TOKEN,
        session=session,
    )


@pytest.fixture
async def api_00(api) -> Paperless:
    """Return a basic Paperless object."""
    async with api:
        yield api


@pytest.fixture
async def api_18(api) -> Paperless:
    """Return a Paperless object with given version."""
    api.version = "1.8.0"
    async with api:
        yield api


@pytest.fixture
async def api_117(api) -> Paperless:
    """Return a Paperless object with given version."""
    api.version = "1.17.0"
    async with api:
        yield api


@pytest.fixture
async def api_20(api) -> Paperless:
    """Return a Paperless object with given version."""
    api.version = "2.0.0"
    async with api:
        yield api


@pytest.fixture
async def api_23(api) -> Paperless:
    """Return a Paperless object with given version."""
    api.version = "2.3.0"
    async with api:
        yield api
