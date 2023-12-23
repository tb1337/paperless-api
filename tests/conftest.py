"""Setup pytest helpers and fixtures."""

import json
import pathlib
from unittest.mock import patch

import pytest

from pypaperless import Paperless


def load_fixture_data(name: str):
    """Load a fixture from disk."""
    path = pathlib.Path(__file__).parent / "fixtures" / name

    content = path.read_text()

    if name.endswith(".json"):
        return json.loads(content)

    return content


@pytest.fixture(scope="session")
def data():
    """Load data."""
    return load_fixture_data("data.json")


@pytest.fixture
async def paperless() -> Paperless:
    """Create and yield client."""

    def endpoints_data():
        d = load_fixture_data("data.json")
        return d["endpoints"]

    api = Paperless("local.test:1337", "secret-key")

    with patch.object(api, "request_json", return_value=endpoints_data()):
        await api.initialize()
    yield api
    await api.close()
