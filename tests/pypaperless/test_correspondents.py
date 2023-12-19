"""Test correspondents."""

from unittest.mock import patch

from pypaperless import Paperless
from pypaperless.api import CorrespondentsEndpoint, EndpointCUDMixin, PaginatedResult
from pypaperless.models import Correspondent
from pypaperless.models.shared import MatchingAlgorithm


async def test_endpoint(paperless: Paperless) -> None:
    """Test endpoint."""
    assert isinstance(paperless.correspondents, CorrespondentsEndpoint)
    assert isinstance(paperless.correspondents, EndpointCUDMixin)


async def test_list_and_get(paperless: Paperless, data):
    """Test list."""
    with patch.object(paperless, "request", return_value=data["correspondents"]):
        result = await paperless.correspondents.list()

        assert isinstance(result, list)
        assert len(result) > 0
        for item in result:
            assert isinstance(item, int)

        page = await paperless.correspondents.get()

        assert isinstance(page, PaginatedResult)
        assert len(page.items) > 0
        assert isinstance(page.items.pop(), Correspondent)


async def test_iterate(paperless: Paperless, data):
    """Test iterate."""
    with patch.object(paperless, "request", return_value=data["correspondents"]):
        async for item in paperless.correspondents.iterate():
            assert isinstance(item, Correspondent)


async def test_one(paperless: Paperless, data):
    """Test one."""
    with patch.object(paperless, "request", return_value=data["correspondents"]["results"][0]):
        item = await paperless.correspondents.one(72)

        assert isinstance(item, Correspondent)
        assert isinstance(item.matching_algorithm, MatchingAlgorithm)
