"""Test correspondents."""

from unittest.mock import patch

import pytest

from pypaperless import Paperless
from pypaperless.controllers import CorrespondentsController
from pypaperless.controllers.base import CreateMixin, DeleteMixin, ResultPage, UpdateMixin
from pypaperless.models import Correspondent
from pypaperless.models.shared import MatchingAlgorithm


@pytest.fixture(scope="module")
def dataset(data):
    """Represent current data."""
    return data["correspondents"]


async def test_endpoint(paperless: Paperless) -> None:
    """Test endpoint."""
    assert isinstance(paperless.correspondents, CorrespondentsController)
    assert isinstance(paperless.correspondents, CreateMixin | UpdateMixin | DeleteMixin)


async def test_list_and_get(paperless: Paperless, dataset):
    """Test list."""
    with patch.object(paperless, "request_json", return_value=dataset):
        result = await paperless.correspondents.list()

        assert isinstance(result, list)
        assert len(result) > 0
        for item in result:
            assert isinstance(item, int)

        page = await paperless.correspondents.get()

        assert isinstance(page, ResultPage)
        assert len(page.items) > 0
        assert isinstance(page.items.pop(), Correspondent)


async def test_iterate(paperless: Paperless, dataset):
    """Test iterate."""
    with patch.object(paperless, "request_json", return_value=dataset):
        async for item in paperless.correspondents.iterate():
            assert isinstance(item, Correspondent)


async def test_one(paperless: Paperless, dataset):
    """Test one."""
    with patch.object(paperless, "request_json", return_value=dataset["results"][0]):
        item = await paperless.correspondents.one(72)

        assert isinstance(item, Correspondent)
        assert isinstance(item.matching_algorithm, MatchingAlgorithm)
