"""Test Tags."""

from unittest.mock import patch

from pypaperless import Paperless
from pypaperless.api import TagsEndpoint
from pypaperless.api.base import BaseEndpointCrudMixin, PaginatedResult
from pypaperless.models import Tag
from pypaperless.models.shared import MatchingAlgorithm


async def test_endpoint(paperless: Paperless) -> None:
    """Test endpoint."""
    assert isinstance(paperless.tags, TagsEndpoint)
    assert isinstance(paperless.tags, BaseEndpointCrudMixin)


async def test_list_and_get(paperless: Paperless, data):
    """Test list."""
    with patch.object(paperless, "request", return_value=data["tags"]):
        result = await paperless.tags.list()

        assert isinstance(result, list)
        assert len(result) > 0
        for item in result:
            assert isinstance(item, int)

        page = await paperless.tags.get()

        assert isinstance(page, PaginatedResult)
        assert len(page.items) > 0
        assert isinstance(page.items.pop(), Tag)


async def test_iterate(paperless: Paperless, data):
    """Test iterate."""
    with patch.object(paperless, "request", return_value=data["tags"]):
        async for item in paperless.tags.iterate():
            assert isinstance(item, Tag)


async def test_one(paperless: Paperless, data):
    """Test one."""
    with patch.object(paperless, "request", return_value=data["tags"]["results"][0]):
        item = await paperless.tags.one(72)

        assert isinstance(item, Tag)
        assert isinstance(item.matching_algorithm, MatchingAlgorithm)
