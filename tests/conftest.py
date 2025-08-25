"""Setup pytest."""

from collections.abc import AsyncGenerator, Generator
from typing import Any

import pytest
from aioresponses import aioresponses

from pypaperless import Paperless
from pypaperless.const import API_PATH

from .const import PAPERLESS_TEST_REQ_ARGS, PAPERLESS_TEST_TOKEN, PAPERLESS_TEST_URL
from .data import DATA_SCHEMA

# mypy: ignore-errors


@pytest.fixture(name="resp")
def aioresponses_fixture() -> Generator[aioresponses]:
    """Return aioresponses fixture."""
    with aioresponses() as m:
        yield m


@pytest.fixture(name="api")
def api_obj_fixture() -> Paperless:
    """Return Paperless."""
    return Paperless(
        PAPERLESS_TEST_URL,
        PAPERLESS_TEST_TOKEN,
        request_args=PAPERLESS_TEST_REQ_ARGS,
    )


@pytest.fixture(name="paperless")
async def paperless_fixture(
    resp: aioresponses,
    api: Paperless,
) -> AsyncGenerator[Paperless, Any]:
    """Return a Paperless object with given version."""
    resp.get(
        f"{PAPERLESS_TEST_URL}{API_PATH['index']}",
        status=200,
        payload=DATA_SCHEMA,
    )
    async with api:
        yield api
