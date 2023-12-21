"""Test storage_paths."""

from unittest.mock import patch

from pypaperless import Paperless
from pypaperless.api import StoragePathsEndpoint
from pypaperless.api.base import BaseEndpointCrudMixin, PaginatedResult
from pypaperless.models import StoragePath
from pypaperless.models.shared import MatchingAlgorithm


async def test_endpoint(paperless: Paperless) -> None:
    """Test endpoint."""
    assert isinstance(paperless.storage_paths, StoragePathsEndpoint)
    assert isinstance(paperless.storage_paths, BaseEndpointCrudMixin)


async def test_list_and_get(paperless: Paperless, data):
    """Test list."""
    with patch.object(paperless, "request", return_value=data["storage_paths"]):
        result = await paperless.storage_paths.list()

        assert isinstance(result, list)
        assert len(result) > 0
        for item in result:
            assert isinstance(item, int)

        page = await paperless.storage_paths.get()

        assert isinstance(page, PaginatedResult)
        assert len(page.items) > 0
        assert isinstance(page.items.pop(), StoragePath)


async def test_iterate(paperless: Paperless, data):
    """Test iterate."""
    with patch.object(paperless, "request", return_value=data["storage_paths"]):
        async for item in paperless.storage_paths.iterate():
            assert isinstance(item, StoragePath)


async def test_one(paperless: Paperless, data):
    """Test one."""
    with patch.object(paperless, "request", return_value=data["storage_paths"]["results"][0]):
        item = await paperless.storage_paths.one(72)

        assert isinstance(item, StoragePath)
        assert isinstance(item.matching_algorithm, MatchingAlgorithm)
