"""Test groups."""

from unittest.mock import patch

import pytest

from pypaperless import Paperless
from pypaperless.api import GroupsEndpoint
from pypaperless.api.base import BaseEndpointCrudMixin, PaginatedResult
from pypaperless.models import Group


@pytest.fixture(scope="module")
def dataset(data):
    """Represent current data."""
    return data["groups"]


async def test_endpoint(paperless: Paperless) -> None:
    """Test endpoint."""
    assert isinstance(paperless.groups, GroupsEndpoint)
    assert not isinstance(paperless.groups, BaseEndpointCrudMixin)


async def test_list_and_get(paperless: Paperless, dataset):
    """Test list."""
    with patch.object(paperless, "request_json", return_value=dataset):
        result = await paperless.groups.list()

        assert isinstance(result, list)
        assert len(result) > 0
        for item in result:
            assert isinstance(item, int)

        page = await paperless.groups.get()

        assert isinstance(page, PaginatedResult)
        assert len(page.items) > 0
        assert isinstance(page.items.pop(), Group)


async def test_iterate(paperless: Paperless, dataset):
    """Test iterate."""
    with patch.object(paperless, "request_json", return_value=dataset):
        async for item in paperless.groups.iterate():
            assert isinstance(item, Group)


async def test_one(paperless: Paperless, dataset):
    """Test one."""
    with patch.object(paperless, "request_json", return_value=dataset["results"][0]):
        item = await paperless.groups.one(72)

        assert isinstance(item, Group)
