"""Setup pytest."""

from collections.abc import AsyncGenerator
from typing import Any

import pytest
from pytest_httpx import HTTPXMock

from pypaperless import Paperless
from pypaperless.const import API_PATH

from .const import PAPERLESS_TEST_TOKEN, PAPERLESS_TEST_URL
from .data import DATA_SCHEMA

# mypy: ignore-errors


@pytest.fixture(name="api")
def api_obj_fixture() -> Paperless:
    """Return Paperless."""
    return Paperless(
        PAPERLESS_TEST_URL,
        PAPERLESS_TEST_TOKEN,
    )


@pytest.fixture(name="paperless")
async def paperless_fixture(
    httpx_mock: HTTPXMock,
    api: Paperless,
) -> AsyncGenerator[Paperless, Any]:
    """Return a Paperless object with given version."""
    httpx_mock.add_response(
        url=f"{PAPERLESS_TEST_URL}{API_PATH['index']}",
        method="GET",
        status_code=200,
        json=DATA_SCHEMA,
    )
    async with api:
        yield api
